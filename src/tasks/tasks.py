from celery import task


@task(name='tasks.tasks.calling_submit')
def calling_submit(instance):
    instance.submitted = True
    instance.save()

