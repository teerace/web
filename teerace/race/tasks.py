from django.db.models import Sum
from race.models import Run, BestRun
from celery.decorators import task


@task(rate_limit='10/m')
def redo_ranks(run_id):
	user_run = Run.objects.get(pk=run_id)
	map_obj = user_run.map
	user_best = BestRun.objects.get(map=map_obj, user=user_run.user)
	if not user_best.run == user_run:
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
	logger = redo_ranks.get_logger()
	logger.info("Processed rank for \"{0}\" map.".format(map_obj))
