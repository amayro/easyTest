from django.shortcuts import render
from django.db import transaction
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView
from django.views.generic.edit import DeleteView
from django.views.generic.base import RedirectView
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
from .models import *
import datetime
import json
from django.core.exceptions import PermissionDenied
from mainapp.forms import TestForm, TestCategoryForm, QuestionForm, AnswerFormSet, GroupForm, StudentForm, StudentEditForm


class StaffPassesTestMixin(UserPassesTestMixin):
    """Миксин делает проверку пользователя на принадлежность к персоналу""" 
    raise_exception = True

    def test_func(self):
        return self.request.user.is_staff


class MainView(TemplateView):
    """Класс отображает главную страницу"""
    template_name = 'mainapp/index.html'


class UsersRedirectView(RedirectView):
    """Класс для автологина пользователей admin или test при нажатии на соответствующую ссылку"""
    pattern_name = 'mainapp:main'

    def get_redirect_url(self, *args, **kwargs):
        slug = self.kwargs['slug']
        user = authenticate(username=slug, password=slug)
        login(self.request, user)
        return super().get_redirect_url()


class QuestionList(LoginRequiredMixin, ListView):
    """docstring for test"""
    model = Question
    login_url = reverse_lazy('authapp:login')
    paginate_by = 1

    def get_queryset(self):
        return self.model.objects.get_test_questions(self.request, self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['test_title'] = self.model.objects.get_test_title(self.kwargs['pk'])
        return context


class QuestionCreate(StaffPassesTestMixin, CreateView):
    """Класс создания вопроса с ответами"""
    model = Question
    form_class = QuestionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['answers'] = AnswerFormSet()
        context['error_messages'] = self.kwargs.get('error_messages')
        if context['error_messages']:
            context['answers'] = AnswerFormSet(self.request.POST)
        return context

    def form_valid(self, form):
        formset = AnswerFormSet(self.request.POST)
        file = self.request.FILES.get('file')

        if file:
            questions = json.load(file)
            answer_model = self.model.answers.rel.related_model

            with transaction.atomic():
                for question in questions:
                    answers = questions[question].pop('answers', None)
                    instance = self.model.objects.create(**questions[question])
                    if answers:
                        for answer in answers:
                            answer_model.objects.create(**answer, question=instance)
                            
            return HttpResponseRedirect(self.get_success_url())

        else:
            if not formset.is_valid():
                self.kwargs['error_messages'] = formset.non_form_errors
                return self.form_invalid(form)
            else:
                formset.instance = form.save()
                return super().form_valid(formset)

    def get_success_url(self):
        return reverse_lazy('mainapp:main')


class TestTimeIsOver(LoginRequiredMixin, ListView):
    template_name = 'mainapp/test_time_is_over.html'
    model = Question


class TestList(LoginRequiredMixin, ListView):
    model = Test
    login_url = reverse_lazy('authapp:login')


class StaffTestList(StaffPassesTestMixin, ListView):
    """Класс для просмотра всех созданных тестов пользователем"""
    model = Test
    template_name = 'mainapp/tests_staff_list.html'

    def get_queryset(self):
        return self.model.objects.get_tests(self.request)


class TestCreate(StaffPassesTestMixin, CreateView):
    """Класс создания нового теста"""
    model = Test
    form_class = TestForm


    def form_valid(self, form):
        file = self.request.FILES.get('file')

        if file:
            tests = json.load(file)
            question_model = self.model.questions.rel.model
            answer_model = question_model.answers.rel.related_model

            with transaction.atomic():
                for test in tests:
                    questions = tests[test].pop('questions', None)
                    instance = self.model.objects.create(**tests[test], owner=self.request.user)
                    questions_list = []
                    for question in questions:
                        answers = question.pop('answers', None)
                        obj = question_model.objects.create(**question)
                        if answers:
                            for answer in answers:
                                answer_model.objects.create(**answer, question=obj)
                        questions_list.append(obj)
                    instance.questions.add(*questions_list)
                            
            return HttpResponseRedirect(self.model.get_absolute_url(self))

        else:
            form.instance.owner = self.request.user
            return super().form_valid(form)


class TestEdit(StaffPassesTestMixin, UpdateView):
    """Класс изменения теста"""
    form_class = TestForm
    model = Test


    def get_success_url(self):
        return reverse_lazy('mainapp:tests_staff')


class TestDelete(StaffPassesTestMixin, DeleteView):
    """Класс удаления теста"""
    model = Test


    def get_success_url(self):
        if self.model.objects.filter(owner=self.request.user).count() == 1:
            return reverse_lazy('mainapp:main')
        else:
            return reverse_lazy('mainapp:tests_staff')


class TestCategoryCreate(StaffPassesTestMixin, CreateView):
    model = TestCategory
    form_class = TestCategoryForm


    def get_success_url(self):
        return reverse_lazy('mainapp:testcategory_list')


class TestCategoryEditView(StaffPassesTestMixin, UpdateView):
    """Класс изменения категории"""
    model = TestCategory
    form_class = TestCategoryForm

    def get_success_url(self):
        return reverse_lazy('mainapp:testcategory_list')


class TestCategoryList(StaffPassesTestMixin, ListView):
    """Класс для просмотра всех созданных категорий тестов пользователем"""
    model = TestCategory
    template_name = 'mainapp/testscategory_list.html'


class TestCategoryDelete(StaffPassesTestMixin, DeleteView):
    """Класс удаления категории теста"""
    model = TestCategory
    success_url = reverse_lazy('mainapp:main')


class ResultCreate(CreateView):
    """docstring for ResultCreate"""
    fields = '__all__'
    model = Result
    slug_url_kwarg = slug_field = 'test'

    def get_success_url(self):
        return reverse_lazy('mainapp:test', kwargs={'pk': self.kwargs['test']})

    def form_valid(self, form):
        Result.objects.get_result_test_queryset(self.request, self.kwargs['test']).hard_delete()
        self.request.session['test_time_begin'] = datetime.datetime.now().timestamp()
        
        form.instance.owner = self.request.user
        form.instance.test = form.fields[self.slug_field].to_python(self.kwargs[self.slug_url_kwarg])
        response = super().form_valid(form)

        self.request.session['test_time'] = datetime.time.strftime(self.object.test.time, '%M:%S')
        for question in self.object.test.questions.all():
            self.kwargs['question'] = question
            self.kwargs['result'] = self.object
            UserAnswerCreate.as_view()(self.request, *self.args, **self.kwargs)

        return response


class ResultList(LoginRequiredMixin, ListView):
    model = Result
    login_url = reverse_lazy('authapp:login')

    def get_queryset(self):
        return self.model.objects.get_results(self.request)


class ResultDetail(LoginRequiredMixin, DetailView):
    """docstring for ResultDetail"""
    model = Result
    slug_field = 'owner'
    login_url = reverse_lazy('authapp:login')

    def get_object(self):
        self.kwargs[self.slug_url_kwarg] = self.request.user
        que = Result.objects.get_result_test_queryset(self.request, self.kwargs['test'])
        response = super().get_object(queryset=que)
        return response

    def get_context_data(self, **kwargs):
        context = {}
        if self.object:
            context['object'] = self.object
            context['user_incorrect_answers'] = self.object.user_answers.get_incorrect_answers()
        context.update(kwargs)
        return super().get_context_data(**context)


class ResultUpdate(ResultDetail, UpdateView):
    """docstring for ResultUpdate"""
    fields = ('right_answers_count', 'wrong_answers_count',)

    def get_object(self):
        response = super().get_object()
        if not response:
            ResultCreate.as_view()(self.request, *self.args, **self.kwargs)
            response = super().get_object()
        self.kwargs['result'] = response
        return response

    def form_valid(self, form):
        self.success_url = self.request.POST['href']
        self.request.session['test_time'] = self.request.POST['left_time']

        if form.instance.active:
            return super().form_valid(form)

        time_result = (datetime.datetime.utcnow() - datetime.timedelta(seconds=self.request.session['test_time_begin'])).time()
        if time_result > self.object.test.time:
            return HttpResponseRedirect(reverse_lazy('mainapp:test_time_is_over', kwargs={'test': self.kwargs['test']}))

        if self.request.POST.get('answer_id') and self.request.POST.get('skip_question', 'False') == 'False':
            pk_list = self.request.POST.getlist('answer_id')
            answer = Answer.objects.get_by_user_ordering(pk_list)
        else:
            answer = ''
            self.success_url = self.request.POST['href_current']

        self.kwargs['answer'] = answer
        self.kwargs['question'] = Question.objects.get(pk=self.request.POST['question_id'])

        UserAnswerUpdate.as_view()(self.request, *self.args, **self.kwargs)

        if self.success_url.startswith('/result'):
            form.instance.active = True
            form.instance.time = time_result
            form.instance.right_answers_count = len(self.object.user_answers.get_correct_answers())
            form.instance.wrong_answers_count = len(self.object.user_answers.get_incorrect_answers())

            if form.instance.right_answers_count >= self.object.test.required_correct_answers:
                form.instance.is_test_passed = True

        response = super().form_valid(form)
        return response


class UserAnswerCreate(CreateView):
    """docstring for UserAnswer Create"""
    fields = '__all__'
    model = UserAnswer

    def form_valid(self, form):
        self.success_url = self.request.POST.get('href', '/')

        form.instance.owner = self.request.user
        form.instance.question = self.kwargs['question']
        form.instance.result = self.kwargs['result']

        return super().form_valid(form)


class UserAnswerUpdate(UpdateView):
    """docstring for UserAnswer Update"""
    fields = ('right_answer', 'user_answer', 'is_correct')
    model = UserAnswer
    slug_field = 'owner'

    def stringificator(self, x_queryset, question_type):
        query_string = ''
        if x_queryset:
            separator = ' - ' if question_type == 'sort' else '; '
            query_string = separator.join([i for i in x_queryset.values_list('description', flat=True)])
        return query_string

    def get_object(self):
        self.kwargs[self.slug_url_kwarg] = self.request.user
        que = UserAnswer.objects.get_queryset_from_question(self.kwargs['question'], self.kwargs['test'])
        try:
            response = super().get_object(queryset=que)
        except:
            UserAnswerCreate.as_view()(self.request, *self.args, **self.kwargs)
            response = super().get_object(queryset=que)
        return response

    def form_valid(self, form):
        self.success_url = self.request.POST['href']
        question_type = self.object.question.q_type

        if question_type == 'select':
            right_answers = self.object.question.answers.get_correct_answer()
            form.instance.is_correct = True if len(self.kwargs['answer']) == len(right_answers) else False
            for each in self.kwargs['answer']:
                if each.is_correct is False or each not in right_answers:
                    form.instance.is_correct = False
        elif question_type == 'sort':
            right_answers = self.object.question.answers.get_enumerated_answers()
            form.instance.is_correct = True if list(self.kwargs['answer']) == list(right_answers) else False

        form.instance.right_answer = self.stringificator(right_answers, question_type)
        form.instance.user_answer = self.stringificator(self.kwargs['answer'], question_type)
        form.instance.active = True if self.kwargs['answer'] else False

        if not form.instance.user_answer:
            form.instance.sort += 1

        return super().form_valid(form)


class GroupList(StaffPassesTestMixin, ListView):
    """docstring for Group ListView"""
    model = Group
    template_name = 'mainapp/group_list.html'


class GroupCreate(StaffPassesTestMixin, CreateView):
    """docstring for Group Create"""
    model = Group
    form_class = GroupForm


    def get_success_url(self):
        return reverse_lazy('mainapp:groups')


class GroupUpdate(StaffPassesTestMixin, UpdateView):
    """docstring for Group Update"""
    model = Group
    form_class = GroupForm


    def get_success_url(self):
        return reverse_lazy('mainapp:groups')


class GroupDelete(StaffPassesTestMixin, DeleteView):
    """docstring for Group Delete"""
    model = Group
    success_url = reverse_lazy('mainapp:groups')


class StudentList(StaffPassesTestMixin, ListView):
    """docstring for Group ListView"""
    model = Student
    template_name = 'mainapp/student_list.html'


class StudentCreate(StaffPassesTestMixin, CreateView):
    """docstring for Group Create"""
    model = Student
    form_class = StudentForm


    def get_success_url(self):
        return reverse_lazy('mainapp:students')


class StudentUpdate(StaffPassesTestMixin, UpdateView):
    """docstring for Group Update"""
    model = Student
    form_class = StudentEditForm


    def get_success_url(self):
        return reverse_lazy('mainapp:students')


class StudentDelete(StaffPassesTestMixin, DeleteView):
    """docstring for Group Delete"""
    model = Student
    success_url = reverse_lazy('mainapp:students')