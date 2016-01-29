from datetime import date, datetime, time, timedelta
from zlib import crc32
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db.models import Sum
from accounts.models import UserProfile
from race.models import Map, MapType, Run, BestRun, Server
from lib.chunks import chunks
from celery.task import task
from tml.tml import Teemap


@task(rate_limit='600/m', ignore_result=True)
def redo_ranks(run_id):
	from brabeion import badges
	
	logger = redo_ranks.get_logger()
	try:
		user_run = Run.objects.get(pk=run_id)
	except Run.DoesNotExist:
		logger.error("[R- /U- /M- ] Run not found (pk={0}).".format(run_id))
		return False
	map_obj = user_run.map
	if user_run.user == None:
		logger.info("[R-{0}/U- /M-{1}] Anonymous run, not"
			" processing the rank.".format(run_id, map_obj.id))
		return
	user_best = BestRun.objects.get(map=map_obj, user=user_run.user)
	if not user_best.run_id == user_run.id:
		logger.info("[R-{0}/U-{1}/M-{2}] Not best run,"
			" not processing the rank.".format(run_id, user_run.user_id, map_obj.id))
		return
	runs = BestRun.objects.filter(map=map_obj)
	# ranked = player that receives points for his place
	ranked_count = len(BestRun.SCORING)
	# exclude banned users from scoring
	ranked = runs.exclude(user__is_active=False)[:ranked_count]
	try:
		if user_run.time >= ranked[ranked_count-1].run.time:
			logger.info("[R-{0}/U-{1}/M-{2}] Run won't affect scoring,"
				" not processing the rank.".format(run_id, user_run.user_id, map_obj.id))
			return
	except IndexError:
		pass
	old_rank = user_run.user.profile.map_position(map_obj.id)
	new_rank = None
	i = 0
	for run in ranked:
		run.points = BestRun.SCORING[i]
		run.save()
		# FIXME it's 3 AM, sorry for that
		run.user.profile.points = BestRun.objects.filter(user=run.user).aggregate(
			Sum('points')
		)['points__sum'] or 0
		run.user.profile.save()
		i += 1
		if user_run.user_id == run.user_id:
			new_rank = i
	runs.exclude(id__in=ranked.values_list('id', flat=True)).update(
		points=0
	)
	badges.possibly_award_badge("rank_processed",
		user=user_run.user)
	logger.info("[R-{0}/U-{1}/M-{2}] {3}'s new map rank is {4} (was: {5})." \
		.format(run_id, user_run.user_id, map_obj.id, user_run.user,
			new_rank, old_rank))


@task(rate_limit='100/m', ignore_result=True)
def rebuild_map_rank(map_id):
	logger = rebuild_map_rank.get_logger()
	try:
		map_obj = Map.objects.get(pk=map_id)
	except Map.DoesNotExist:
		logger.error("[M- ] Map not found (pk={0}).".format(map_id))
		return False
	runs = BestRun.objects.filter(map=map_obj)
	# ranked = player that receives points for his place
	ranked_count = len(BestRun.SCORING)
	# exclude banned users from scoring
	ranked = runs.exclude(user__is_active=False)[:ranked_count]
	i = 0
	for run in ranked:
		run.points = BestRun.SCORING[i]
		run.save()
		i += 1
	runs.exclude(id__in=ranked.values_list('id', flat=True)).update(
		points=0
	)
	logger.info("[M-{0}] Rebuilt rank for map \"{0}\"." \
		.format(map_id, map_obj.name))


@task(rate_limit='10/m', ignore_result=True)
def rebuild_global_rank():
	runners = User.objects.annotate(Sum('bestrun__points'))
	for runner in runners:
		runner.profile.points = runner.bestrun__points__sum or 0
		runner.profile.save()
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
		logger.error("[M- ] Map not found (pk={0}).".format(map_id))
		return False
	try:
		# I actually can use that! Thanks, erd!
		teemap = Teemap(map_obj.map_file.path)
		logger.info("[M-{0}] Loaded \"{1}\" map.".format(map_id, map_obj.name))
	except IndexError:
		logger.error("[M-{0}] Couldn't load \"{1}\" map" \
			.format(map_id, map_obj.name))
		has_unhookables = has_deathtiles = None
		shield_count = heart_count = grenade_count = None
	else:
		has_unhookables = has_deathtiles = is_fastcap = has_teleporters = \
			has_speedups = False
		shield_count = heart_count = grenade_count = 0
		logger.info("Counting map items...")
		for tile in teemap.gamelayer.tiles:
			if tile.index == indexes.DEATHTILE:
				has_deathtiles = True
			elif tile.index == indexes.UNHOOKABLE:
				has_unhookables = True
			elif tile.index == indexes.SHIELD:
				shield_count += 1
			elif tile.index == indexes.HEART:
				heart_count += 1
			elif tile.index == indexes.GRENADE:
				grenade_count += 1
		if teemap.telelayer:
			has_teleporters = True
		if teemap.speeduplayer:
			has_speedups = True

		# DISABLED due to huge (counted in GiBs) memory usage
		# logger.info("Rendering map screenshot.")
		# map_image = teemap.render(gamelayer_on_top=True)
		# map_image.save('{0}images/maps/full/{1}.png'.format(settings.MEDIA_ROOT,
		# 	map_obj.name))
		# logger.info("Finished rendering map screenshot.")
		# map_obj.has_image = True

	map_obj.has_unhookables = has_unhookables
	map_obj.has_deathtiles = has_deathtiles
	map_obj.has_teleporters = has_teleporters
	map_obj.has_speedups = has_speedups

	map_map_types = map_obj.map_types.filter(slug='fastcap-no-weapons')
	if not map_map_types:
		map_obj.shield_count = shield_count
		map_obj.heart_count = heart_count
		map_obj.grenade_count = grenade_count
	logger.info("Finished counting map items.")

	logger.info("Generating map CRC...")
	map_obj.map_file.open()
	map_obj.crc = '{0:x}'.format(crc32(map_obj.map_file.read()) & 0xffffffff)
	map_obj.map_file.close()
	map_obj.save()

	map_map_types = map_obj.map_types.filter(slug='fastcap')
	if map_map_types:
		logger.info("Creating a non-weapon twin...")
		new_map, created = Map.objects.get_or_create(
			name="{0}-no-weapons".format(map_obj.name),
			defaults={
				'author': map_obj.author,
				'added_by': map_obj.added_by,
				'map_file' :map_obj.map_file,
				'crc': map_obj.crc,
				'has_unhookables': has_unhookables,
				'has_deathtiles': has_deathtiles,
			})
		if not created:
			logger.info("Oh, it already exists! Updating...")
			new_map.author = map_obj.author
			new_map.added_by = map_obj.added_by
			new_map.map_file = map_obj.map_file
			new_map.crc = map_obj.crc
			new_map.has_unhookables = has_unhookables
			new_map.has_deathtiles = has_deathtiles
			new_map.save()
		else:
			new_map.map_types.add(MapType.objects.get(slug='fastcap-no-weapons'))
			new_map.map_types.add(*map_obj.map_types.exclude(slug='fastcap'))
			new_map.save()
	logger.info("[M-{0}] Finished processing \"{1}\" map." \
		.format(map_id, map_obj.name))


@task(ignore_result=True)
def set_server_map(server_id, map_id):
	logger = set_server_map.get_logger()
	try:
		map_obj = Map.objects.get(pk=map_id)
	except Map.DoesNotExist:
		logger.error("[S-{0}/M- ] Map not found (pk={1}).".format(server_id, map_id))
		return False
	try:
		server = Server.objects.get(pk=server_id)
	except Server.DoesNotExist:
		logger.error("[S- /M-{1}] Server not found (pk={0}).".format(server_id, map_id))
		return False
	if server.played_map == map_obj:
		logger.info("[S-{0}/M-{1}] Map already set"
			" as currently played.".format(server_id, map_id))
		return
	else:
		old_map_id = server.played_map_id
	server.played_map = map_obj
	server.save()
	logger.info("[S-{0}/M-{1}] Map set"
		" as currently played (was: M-{2}).".format(server_id, map_id, old_map_id))


@task(ignore_result=True)
def update_user_points_history():
	# everyday, around 4:30 AM
	users = UserProfile.objects.values_list('id', flat=True)
	for chunk in list(chunks(users, 200)):
		update_user_points_history_chunked.delay(chunk)


@task(ignore_result=True)
def update_user_points_history_chunked(chunk):
	yesterday = date.today() - timedelta(1)
	for user_id in chunk:
		user = UserProfile.objects.get(pk=user_id)
		if not user.points_history:
			# let's make a list
			user.points_history = []
		elif user.points_history[-1][0] == yesterday:
			# making sure we save only one time per day
			continue
		user.yesterday_points = user.points
		user.points_history.append((yesterday, user.points))
		user.save()


@task(ignore_result=True)
def update_yesterday_runs():
	# everyday, around 0:00 AM
	yesterday = datetime.today() - timedelta(days=1)
	runs_yesterday = Run.objects.filter(created_at__range=
		(datetime.combine(yesterday, time.min),
		datetime.combine(yesterday, time.max)))
	cache.set('runs_yesterday', runs_yesterday, timeout=None)


@task(ignore_result=True)
def update_totals():
	# every 15 minutes
	total_runs = Run.objects.count()
	total_runtime = Run.objects.aggregate(Sum('time'))['time__sum']
	total_playtime = UserProfile.objects.aggregate(
		Sum('playtime')
	)['playtime__sum']
	cache.set('total_runs', total_runs, timeout=None)
	cache.set('total_runtime', total_runtime, timeout=None)
	cache.set('total_playtime', total_playtime, timeout=None)
