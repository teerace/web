from zlib import crc32
from django.conf import settings
from django.db.models import Sum
from accounts.models import UserProfile
from race.models import Map, Run, BestRun
from celery.decorators import task
from celery.task.sets import subtask
from tml.tml import Teemap


@task(rate_limit='10/m', ignore_result=True)
def redo_ranks(run_id):
	logger = redo_ranks.get_logger()
	try:
		user_run = Run.objects.get(pk=run_id)
	except Run.DoesNotExist:
		logger.error("How is that possible? (Run doesn't exist)")
	map_obj = user_run.map
	user_best = BestRun.objects.get(map=map_obj, user=user_run.user)
	if not user_best.run_id == user_run.id:
		return
	runs = BestRun.objects.filter(map=map_obj)
	# ranked = player that receives points for his place
	ranked_count = len(BestRun.SCORING)
	# exclude anonymous user from scoring
	ranked = runs.exclude(user__pk=0)
	ranked = ranked.order_by('run__time')[:ranked_count]
	try:
		if user_run.time >= ranked[ranked_count-1].run.time:
			return
	except IndexError:
		pass
	c = 0
	for run in ranked:
		run.points = BestRun.SCORING[c]
		run.save()
		# FIXME it's 3 AM, sorry for that
		run.user.profile.points = BestRun.objects.filter(user=run.user).aggregate(
			Sum('points')
		)['points__sum']
		run.user.profile.save()
		c += 1
	runs.exclude(id__in=ranked.values_list('id', flat=True)).update(
		points=0
	)
	logger.info("Processed rank for \"{0}\" map.".format(map_obj))


@task(rate_limit='10/m', ignore_result=True)
def rebuild_map_rank(map_id):
	map_obj = Map.objects.get(pk=map_id)
	runs = BestRun.objects.filter(map=map_obj)
	# ranked = player that receives points for his place
	ranked_count = len(BestRun.SCORING)
	# exclude anonymous user from scoring
	ranked = runs.exclude(user__pk=0).order_by('run__time')[:ranked_count]
	for run in ranked:
		run.points = BestRun.SCORING[c]
		run.save()
		c += 1
	runs.exclude(id__in=ranked.values_list('id', flat=True)).update(
		points=0
	)
	logger = rebuild_map_rank.get_logger()
	logger.info("Rebuilt rank for map \"{0}\".".format(map_obj.name))


@task(rate_limit='1/m', ignore_result=True)
def rebuild_global_rank():
	# FIXME oh man, fix me.
	runners = UserProfile.objects.exclude(user__pk=0)
	for runner in runners:
		runner.points = BestRun.objects.filter(user=runner.user).aggregate(
			Sum('points')
		)['points__sum'] or 0
		runner.save()
	logger = rebuild_global_rank.get_logger()
	logger.info("Rebuilt global rank.")


class index_factory(object):
	INDEXES = dict(
		DEATHTILE = 2,
		UNHOOKABLE = 3,
		RED_FLAG = 195,
		BLUE_FLAG = 196,
		SHIELD = 197,
		HEART = 198,
		GRENADE = 200,
	)

	def __getattr__(self, attr):
		try:
			return self.INDEXES.get(attr)
		except TypeError:
			raise AttributeError(attr)
indexes = index_factory()


@task(ignore_result=True)
def retrieve_map_details(map_id):
	"""
	WARNING!
	This task is CPU/(and highly) RAM expensive.
	
	Checks for presence of specified tiles, counts some of them
	and at the end takes a beautiful photo of the map.
	
	Thanks for your help, erdbeere!
	"""
	logger = retrieve_map_details.get_logger()
	try:
		map_obj = Map.objects.get(pk=map_id)
	except Map.DoesNotExist:
		logger.error("Are you kidding me? (map doesn't exist)")

	# I actually can use that! Thanks, erd!
	teemap = Teemap().load(map_obj.map_file.path)
	logger.info("Loaded \"{0}\" map.".format(map_obj.name))

	logger.info("Counting map items...")
	has_unhookables = has_deathtiles = is_fastcap = False
	shield_count = heart_count = grenade_count = 0
	for tile in teemap.gamelayer.tiles:
		if tile.index == indexes.DEATHTILE:
			has_deathtiles = True
		elif tile.index == indexes.UNHOOKABLE:
			has_unhookables = True
		elif tile.index in (indexes.RED_FLAG, indexes.BLUE_FLAG):
			is_fastcap = True
		elif tile.index == indexes.SHIELD:
			shield_count += 1
		elif tile.index == indexes.HEART:
			heart_count += 1
		elif tile.index == indexes.GRENADE:
			grenade_count += 1
	map_obj.has_unhookables = has_unhookables
	map_obj.has_deathtiles = has_deathtiles
	map_obj.shield_count = shield_count
	map_obj.heart_count = heart_count
	map_obj.grenade_count = grenade_count
	logger.info("Finished counting map items.")

	# DISABLED due to huge (counted in GiBs) memory usage
	# logger.info("Rendering map screenshot.")
	# map_image = teemap.render(gamelayer_on_top=True)
	# map_image.save('{0}images/maps/full/{1}.png'.format(settings.MEDIA_ROOT,
	# 	map_obj.name))
	# logger.info("Finished rendering map screenshot.")
	# map_obj.has_image = True

	logger.info("Generating map CRC...")
	map_obj.crc = '{0:x}'.format(crc32(map_obj.map_file.read()) & 0xffffffff)
	map_obj.map_file.close()

	if is_fastcap:
		logger.info("Turning map into fastcap type...")
		map_obj.map_type = Map.MAP_FASTCAP
		logger.info("Creating a non-weapon twin...")
		new_map = Map(
			name="{0}-noweapon".format(map_obj.name),
			author=map_obj.author,
			added_by=map_obj.added_by,
			map_file=map_obj.map_file,
			crc=map_obj.crc,
			map_type=Map.MAP_FASTCAP_NO_WEAPONS,
			has_unhookables=has_unhookables,
			has_deathtiles=has_deathtiles,
		)
		new_map.save()
	map_obj.save()
	logger.info("Finished processing \"{0}\" map.".format(map_obj.name))
