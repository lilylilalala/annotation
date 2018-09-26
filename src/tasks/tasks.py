from celery import task


@task(name='tasks.tasks.calling_commit')
def calling_commit(instance):
    instance.committed = True
    instance.save()

