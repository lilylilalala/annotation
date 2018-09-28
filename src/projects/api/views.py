import os
import csv

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.files.base import ContentFile
from rest_framework.response import Response
from rest_framework import generics, mixins, permissions

from projects.models import Project, Status
from .serializers import (
    ProjectSerializer,
    ProjectInlineUserSerializer,
    ProjectInlineVerifySerializer,
    ProjectTargetSerializer,
    ProjectReleaseSerializer,
    ProjectResultURLSerializer,
)
from tasks.api.serializers import (
    TaskResultSerializer,
    ContributeResultSerializer,
    InspectResultSerializer,
)
from accounts.api.permissions import IsOwnerOrReadOnly, IsStaff
from accounts.api.users.serializers import UserInlineSerializer, EditContributorsSerializer


User = get_user_model()


class ProjectAPIView(mixins.CreateModelMixin, generics.ListAPIView):
    """
    get:
        【任务管理】 获取所有状态为“进行中”的公有任务列表

    post:
        【任务管理】 新建任务
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = ProjectSerializer
    queryset = Project.objects.filter(private=False, status='answering')
    passed_id = None

    search_fields = ('project_type', 'founder__email')
    ordering_fields = ('project_type', 'timestamp')
    filter_fields = ('project_type',)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(founder=self.request.user)


class ProjectAPIDetailView(mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.RetrieveAPIView):
    """
    get:
        【任务管理】or【任务广场】 获取任务详情

    put:
        【任务管理】 编辑任务

    patch:
        【任务管理】 编辑任务

    delete:
        【任务管理】 删除任务
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = ProjectInlineUserSerializer
    queryset = Project.objects.all()
    lookup_field = 'id'

    def validate_status(self):
        project_id = self.kwargs.get("id", None)
        project = Project.objects.get(id=project_id)
        if project.project_status in ['unreleased', 'failed']:
            return True

    def put(self, request, *args, **kwargs):
        if self.validate_status():
            return self.update(request, *args, **kwargs)
        else:
            return Response({"detail": "Not allowed here"}, status=400)

    def patch(self, request, *args, **kwargs):
        if self.validate_status():
            return self.update(request, *args, **kwargs)
        else:
            return Response({"detail": "Not allowed here"}, status=400)

    def delete(self, request, *args, **kwargs):
        if self.validate_status():
            return self.destroy(request, *args, **kwargs)
        else:
            return Response({"detail": "Not allowed here"}, status=400)


class ProjectReleaseView(generics.RetrieveAPIView, mixins.UpdateModelMixin):
    """
    get:
        【任务管理】 获取任务详情

    put:
        【任务管理】 发布任务（只有状态为未发布和未通过的任务可以进行发布操作）
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = ProjectReleaseSerializer
    queryset = Project.objects.all()
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        project = Project.objects.get(id=project_id)
        if project.project_status in ['unreleased', 'failed']:
            Project.objects.filter(id=project.id).update(status='verifying')
            return self.get(self, request, *args, **kwargs)
        else:
            return Response({"detail": "Not allowed here"}, status=400)


class ContributorsListView(generics.ListAPIView, mixins.UpdateModelMixin):
    """
    get:
        【参与任务】 获取当前任务的标注人列表

    put:
        【参与任务】 参与或退出任务
            若当前用户不在标注人列表中，通过put方法参与该任务；若当前用户在标注人列表中，通过put方法退出该任务
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = UserInlineSerializer

    search_fields = ('email', 'full_name')
    ordering_fields = ('email', 'full_name')

    def get_queryset(self, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        if project_id is None:
            return User.objects.none()
        project = Project.objects.get(id=project_id)
        return project.contributors.all()

    def put(self, request, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        project = Project.objects.get(id=project_id)
        user = request.user
        if user in project.contributors.all():
            project.contributors.remove(user)
            return Response({"message": "You have successfully exited the project!"}, status=200)
        else:
            project.contributors.add(user)
            return Response({"message": "You have successfully entered the project!"}, status=200)


class ProjectAddContributorsView(generics.ListAPIView, mixins.UpdateModelMixin):
    """
    get:
        【成员管理】 获取未参与任务的成员列表

    put:
        【添加成员】 添加标注人
            获取用户id，若该用户不在标注人列表中，通过put方法在标注人列表在添加该用户；
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = EditContributorsSerializer

    search_fields = ('email', 'full_name')
    ordering_fields = ('email', 'full_name')

    def get_queryset(self, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        if project_id is None:
            return User.objects.none()
        return User.objects.exclude(contributed_projects=project_id)

    def put(self, request, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        project = Project.objects.get(id=project_id)
        user_id = request.data.get("user_id")
        user = get_object_or_404(User, id=user_id)
        if user is None:
            return Response({"message": "User does not exist"}, status=400)
        if user not in project.contributors.all():
            project.contributors.add(user)
            return Response({"message": "User has successfully entered the project!"}, status=200)
        else:
            return Response({"message": "User is already in the project!"}, status=400)


class ProjectDeleteContributorsView(generics.ListAPIView, mixins.UpdateModelMixin):
    """
    get:
        【成员管理】 获取任务的标注人列表

    put:
        【删除成员】 删除标注人
            获取用户id，若该用户在标注人列表中，通过put方法从标注人列表中删除该用户
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = EditContributorsSerializer

    search_fields = ('email', 'full_name')
    ordering_fields = ('email', 'full_name')

    def get_queryset(self, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        if project_id is None:
            return User.objects.none()
        project = Project.objects.get(id=project_id)
        return project.contributors.all()

    def put(self, request, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        project = Project.objects.get(id=project_id)
        user_id = request.data.get("user_id")
        user = get_object_or_404(User, id=user_id)
        if user is None:
            return Response({"message": "User does not exist"}, status=400)
        if user in project.contributors.all():
            project.contributors.remove(user)
            return Response({"message": "User has successfully exited the project!"}, status=200)
        else:
            return Response({"message": "User is NOT in the project!"}, status=400)


class ProjectVerifyListView(generics.ListAPIView):
    """
    get:
        【任务审核】 获取状态为“审核中”or“已通过”or“未通过”的任务列表
    """
    Permission_classes = [IsStaff]
    serializer_class = ProjectSerializer

    search_fields = ('project_type', 'founder__email')
    ordering_fields = ('project_type', 'timestamp')
    filter_fields = ('status',)

    queryset = Project.objects.exclude(status='unreleased')


class ProjectVerifyDetailView(generics.RetrieveAPIView, mixins.UpdateModelMixin):
    """
    get:
        【任务审核】 获取审核中的任务详情

    put:
        【任务审核】 修改审核状态为“通过”或“不通过”
    """
    Permission_classes = [IsStaff]
    serializer_class = ProjectInlineVerifySerializer

    def get_object(self, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        project = get_object_or_404(Project, id=project_id)
        return project

    def put(self, request, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        project = get_object_or_404(Project, id=project_id)
        if project.project_status != 'verifying':
            return Response({"detail": "Not allowed here"}, status=400)
        verify_status = request.data['verify_status']
        if verify_status == 'passed':
            Project.objects.filter(id=project.id).update(status='answering')
        else:
            Project.objects.filter(id=project.id).update(status='failed')
        return self.get(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.put(request, *args, **kwargs)

    def perform_update(self, serializer):
        serializer.save(verify_staff=self.request.user)


class ProjectTargetDetailView(generics.RetrieveAPIView, mixins.UpdateModelMixin):
    """
    get:
        【任务管理】 获取任务目标

    put:
        【任务管理】 更改任务目标

    patch:
        【任务管理】 更改任务目标
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = ProjectTargetSerializer
    queryset = Project.objects.all()
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class ProjectResultView(generics.ListAPIView):
    """
    get:
        【任务管理】 获取任务结果详情
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = TaskResultSerializer

    search_fields = ()
    ordering_fields = ('id', 'updated',)
    filter_fields = ('label',)

    def get_queryset(self, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        project = get_object_or_404(Project, id=project_id)
        return project.task_set.exclude(label='')


class ProjectMyContributionView(generics.ListAPIView):
    """
    get:
        【参与任务】 获取标注人已答过的题目
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ContributeResultSerializer

    search_fields = ()
    ordering_fields = ('id', 'created', 'updated',)
    filter_fields = ('label',)

    def get_queryset(self, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        project = get_object_or_404(Project, id=project_id)
        user = self.request.user
        if user is None:
            return Project.task_set.none()
        return project.contribution_set.filter(contributor=user)


class ProjectMyInspectionView(generics.ListAPIView):
    """
    get:
        【检查任务】 获取质检人已答过的题目
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InspectResultSerializer

    search_fields = ()
    ordering_fields = ('id', 'created', 'updated',)
    filter_fields = ('label',)

    def get_queryset(self, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        project = get_object_or_404(Project, id=project_id)
        user = self.request.user
        if user is None:
            return Project.task_set.none()
        return project.inspection_set.filter(inspector=user)


class ProjectResultDownloadView(generics.RetrieveAPIView):
    """
    get:
        获取任务结果文件链接
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = ProjectResultURLSerializer
    lookup_field = 'id'

    def create_result_file(self, instance):
        try:
            file_name = '%s_%s_%s_result.csv' % (instance.id, instance.name, instance.project_type)
            instance.result_file.save(file_name, ContentFile('RESULT'))
            f = open(os.path.join(settings.RESULT_ROOT, file_name), mode='w', encoding='utf-8', newline='')
            queryset = instance.task_set.all()

            for i, obj in enumerate(queryset):
                path = obj.file_path
                reader = csv.DictReader(open(path, encoding='utf-8'))
                fieldnames = reader.fieldnames
                fieldnames.append('label')
                if i == 0:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                for row in reader:
                    row['label'] = obj.label
                    writer.writerow(row)
        except:
            #instance.result_file.delete()
            return Response({"message": "Fail to create result file!"}, status=400)

    def get(self, request, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        project = get_object_or_404(Project, id=project_id)
        if project.project_status == 'completed':
            if not project.result_file:
                self.create_result_file(project)
            serializer = self.get_serializer(project)
            return Response(serializer.data)
        else:
            return Response({"message": "Project is not completed"}, status=400)


class InspectorsListView(generics.RetrieveAPIView, mixins.UpdateModelMixin):
    """
    get:
        【检查任务】 获取当前任务的标注人
    put:
        【更新检查人】 根据提交的user_id，通过put方法更新project的检查人
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = EditContributorsSerializer

    search_fields = ('email', 'full_name')
    ordering_fields = ('email', 'full_name')

    def get_object(self, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        project = get_object_or_404(Project, id=project_id)
        if project.inspector:
            return project.inspector
        return User.objects.none()

    def put(self, request, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        project = Project.objects.get(id=project_id)
        user_id = request.data.get("user_id")
        user = get_object_or_404(User, id=user_id)
        project_type = project.project_type.type.name
        if project_type == 'Classification':
            if project.repetition_rate != 1.0:
                if user == project.inspector:
                    return Response({"message": "User is already in the project!"}, status=400)
                else:
                    Project.objects.filter(id=project_id).update(inspector=user)
                    return Response({"message": "User has updated in the project!"}, status=200)
            else:
                return Response({"message": "No inspector since repetition rate is 1.0"}, status=400)
        else:
            return Response({"message": "Only Classification projects have a inspector"}, status=400)
