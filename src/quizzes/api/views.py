from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import generics, mixins, permissions

from django.http import HttpResponse
import csv
from django.utils.encoding import escape_uri_path
from quizzes.models import Quiz, QuizContributor, Answer, QuestionType
from .serializers import (
    QuizSerializer,
    QuestionSerializer,
    AnswerSerializer,
    QuizRecordSerializer,
    QuestionsAddSerializer,
    AnswerUpdateSerializer,
    QuestionSubmitSerializer,
    QuestionTypeSerializer,
)
from accounts.api.permissions import IsOwner, IsOwnerOrReadOnly
import django.utils.timezone as timezone


class QuizAPIView(mixins.CreateModelMixin, generics.ListAPIView):
    """
    get:
        【测试题管理】 获取测试题列表

    post:
        【测试题管理】 新建测试题
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = QuizSerializer
    queryset = Quiz.objects.all()

    search_fields = ('name', 'founder__email')
    ordering_fields = ('quiz_type', 'timestamp')
    filter_fields = ('quiz_type',)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(founder=self.request.user)


class QuizAPIDetailView(generics.RetrieveAPIView, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    """
    get:
        【测试题管理】 获取测试题详情

    put:
        【测试题管理】 编辑测试题

    delete:
        【测试题管理】 删除测试题
    """
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = QuizSerializer
    queryset = Quiz.objects.all()
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):
        quiz_id = self.kwargs.get("id", None)
        quiz_file = request.data.get("quiz_file", None)
        label_file = request.data.get("label_file", None)
        if quiz_file and label_file:
            quiz = get_object_or_404(Quiz, id=quiz_id)
            question = quiz.question_set.all()
            question.delete()
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class QuestionsAddAPIView(generics.RetrieveAPIView, mixins.UpdateModelMixin):
    """
    get:
        【测试题管理】 获取测试题详情

    put:
        【测试题管理】 上传一个新的quiz文件,在原先的题目不删除的情况下添加
    """
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    serializer_class = QuestionsAddSerializer
    queryset = Quiz.objects.all()
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class QuestionAPIView(generics.ListAPIView):
    """
    get:
        【测试题管理】 获取测试题详情，只有创建测试题的人可以看

    put:
        【测试题管理】 删除指定的一道题目
    """
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    serializer_class = QuestionSerializer

    search_fields = ()
    ordering_fields = ()

    def get_queryset(self, *args, **kwargs):
        quiz_id = self.kwargs.get("id", None)
        quiz = get_object_or_404(Quiz, id=quiz_id, founder=self.request.user)
        return quiz.question_set.all()

    def put(self, request, *args, **kwargs):
        quiz_id = self.kwargs.get("id", None)
        quiz = get_object_or_404(Quiz, id=quiz_id, founder=self.request.user)
        question_id = request.data.get("question_id")
        if question_id:
            question = quiz.question_set.get(id=question_id)
            question.delete()
        else:
            return Response({"message": "Question_id should not be empty"}, status=400)


class QuestionDownloadAPIView(generics.ListAPIView):
    """
    get:
        【测试题管理】 下载测试题
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = QuestionSerializer

    def get(self, request, *args, **kwargs):
        quiz_id = self.kwargs.get("id", None)
        quiz = get_object_or_404(Quiz, id=quiz_id, founder=request.user)
        return self.download_file(quiz)

    def download_file(self, instance):
        queryset = instance.question_set.all()
        response = HttpResponse(content_type='text/csv')
        name = '%s_%s_%s.csv' % (instance.id, instance.name, instance.quiz_type)
        response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(escape_uri_path(name))
        print(response['Content-Disposition'])
        writer = csv.writer(response)
        for i, obj in enumerate(queryset):
            path = obj.file_path
            reader = csv.reader(open(path, encoding='utf-8'))
            if i == 0:
                for j, row in enumerate(reader):
                    if j == 0:
                        row.append('label')
                        writer.writerow(row)
                    else:
                        row[0] = i
                        row.append(obj.label)
                        writer.writerow(row)
            else:
                for j, row in enumerate(reader):
                    if j == 1:
                        row[0] = i
                        row.append(obj.label)
                        writer.writerow(row)
        return response


class AnswerAPIView(generics.RetrieveAPIView, mixins.UpdateModelMixin):
    """
    get:
        【参与任务】 获取一道测试题

    put:
        【参与任务】 答题，给问题添加目标标签

    patch:
        【参与任务】 答题，给问题添加目标标签
    """
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = AnswerSerializer

    def get_object(self, *args, **kwargs):
        quiz_id = self.kwargs.get("id", None)
        user = self.request.user
        qc = QuizContributor.objects.get(quiz_id=quiz_id, contributor=user)
        spare_set = Answer.objects.filter(quiz_contributor=qc, label='')
        if spare_set:
            return spare_set.first()
        return Answer.objects.none().first()

    def get(self, request, *args, **kwargs):
        quiz_id = self.kwargs.get("id", None)
        quiz = get_object_or_404(Quiz, id=quiz_id)
        user = request.user
        if user not in quiz.contributors.all():
            qc = QuizContributor(quiz=quiz, contributor=user)
            qc.save()
        instance = self.get_object()
        quizcontributor = QuizContributor.objects.get(quiz_id=quiz_id, contributor=user)
        if instance:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        if quizcontributor.is_completed:
            return Response({"message": "All questions have been answered,Please check and submit!"}, status=200)
        elif quizcontributor.status == 'submitted':
            return Response({"message": "Quiz submitted"}, status=200)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            if request.data['label']:
                instance.label = request.data['label']
                if not instance.created:
                    instance.created = timezone.now()
                instance.save()
        return self.get(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class QuizRecordView(generics.ListAPIView):
    """
    get:
        【测试题管理】 获取一个测试题的答题记录
    """

    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = QuizRecordSerializer

    ordering_fields = ('accuracy', 'updated', 'status')
    filter_fields = ('status',)

    def get_queryset(self, *args, **kwargs):
        quiz_id = self.kwargs.get("id", None)
        quiz = get_object_or_404(Quiz, id=quiz_id)
        return quiz.quizcontributor_set.all()


class AnswerUpdateAPIView(generics.RetrieveAPIView, mixins.UpdateModelMixin):
    """
    get:
        【参与任务】 获取未提交测试题中已答的一道测试题

    put:
        【参与任务】 根据id，对已答的一道测试题更改标签
    """
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = AnswerUpdateSerializer
    queryset = Quiz.objects.all()
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        quiz_id = self.kwargs.get("id", None)
        answerid = self.kwargs.get("answerid", None)
        quizcontributor = QuizContributor.objects.get(quiz_id=quiz_id, contributor_id=self.request.user)
        instance = Answer.objects.get(quiz_contributor=quizcontributor, id=answerid)
        if quizcontributor.status != 'submitted':
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response({"message": "Quiz submitted,Don't update"}, status=400)

    def put(self, request, *args, **kwargs):
        answerid = self.kwargs.get("answerid", None)
        if request.data['label']:
            instance = get_object_or_404(Answer, id=answerid)
            instance.label = request.data['label']
            instance.save()
        else:
            return Response({"message": "Label should not be empty"}, status=400)


class QuestionSubmitAPIView(generics.RetrieveAPIView):
    """
    get:
        【参与任务】 获取当前的做题进度（已提交会显示做题得分）

    put:
        【参与任务】 提交测试题并计算得分（未完成全部测试题不能提交）
    """
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = QuestionSubmitSerializer
    queryset = Quiz.objects.all()
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        quiz_id = self.kwargs.get("id", None)
        instance = QuizContributor.objects.get(quiz_id=quiz_id, contributor_id=request.user)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        quiz_id = self.kwargs.get("id", None)
        qc = QuizContributor.objects.get(quiz_id=quiz_id, contributor_id=request.user)
        if qc.status == 'in progress':
            if qc.is_completed:
                qc.status = 'submitted'
                if not qc.accuracy:
                    good_answer = 0
                    for answer in Answer.objects.filter(quiz_contributor=qc):
                        if answer.label == answer.question.label:
                            good_answer += 1
                    qc.accuracy = good_answer / qc.quantity
                qc.save()
                return self.get(request, *args, **kwargs)
            else:
                uncompleted = Answer.objects.filter(quiz_contributor=qc, label='').count()
                return Response({"message": "%s questions remain unanswered,Can't be submitted" % uncompleted}, status=400)
        else:
            return Response({"message": "Quiz submitted"}, status=400)


class QuestionTypeAPIView(generics.ListAPIView):
    """
    get:
        【任务管理】 获取任务类型列表
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = QuestionTypeSerializer
    queryset = QuestionType.objects.all()
