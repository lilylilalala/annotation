### 第一阶段需求
0. 用户角色
- 标注用户
    - not staff, not admin
    - 参与项目
    - 创建项目
- 项目审核员
    - is staff, not admin
    - 查看待审核项目信息
    - 审核项目
- 系统管理员
    - is staff, is admin

1. 用户新建标注项目
- 提供项目类型，项目属性，项目摘要，项目截止时间等参数

2. 用户编辑项目
- 修改项目摘要，项目截止时间等参数

3. 用户新建任务
- 任务继承项目的类型、属性、摘要等信息
- 上传标注文件
- 显示目标列表，从中选择标注目标

4. 用户编辑任务
- 验证任务审核状态（审核中、审核通过后不能编辑任务信息）
- 验证任务从属权限
- 修改任务的名称、标注文件、标注目标等

5. 用户发布任务
- 任务进入待审核状态

6. 任务审核
- 系统审核员审核任务
    - 审核通过，任务正式发布
    - 审核不通过，任务发布失败

7. 发起人邀请标注人（私有任务）
- 在标注人列表中勾选若干标注人，标注人同意后正式参与项目

8. 发起人选择标注人（公有任务）
- 显示已报名该任务的标注人列表
- 审核通过，标注人报名成功，进入任务
- 审核不通过，标注人报名失败

9. 删除标注人
- 验证标注人答题状态（已经答题的标注人不能从任务中删除）

10. 标注人报名
- 进入报名审核状态

11. 标注人答题
- 每一页显示一道题，翻页时自动保存

12. 任务完成
- 题目全部答完即完成
- 发起人、标注人各自的项目状态更新为已完成

13. 查看结果
- 显示每道题的答案、标注人

14. 新增目标
- 提供三种类型的目标（类目、关键词、实体）
- 类目目标为若干个词
- 实体目标为若干个词
- 关键词目标为一段描述

15. 编辑目标
- 可修改目标名称、说明和目标下包含的词语



### 第一阶段接口
0. User register
- /api/auth/register/
- post
- required_fields
    - emial
    - full_name
    - phone_number
    - password
    - password2
- response

        HTTP 201 Created
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept
        
        {
            "email": "tree@gmail.com",
            "full_name": "tree",
            "phone_number": "15611111112",
            "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo0LCJ1c2VybmFtZSI6InRyZWVAZ21haWwuY29tIiwiZXhwIjoxNTI3NjQ5MzU5LCJlbWFpbCI6InRyZWVAZ21haWwuY29tIiwib3JpZ19pYXQiOjE1Mjc2NDkwNTl9.7B6M7k3yesN2ZxLnU321rD2EtWB2RZzr9-ujspTx0vs",
            "expires": "2018-06-06T10:54:19.918719",
            "message": "Thank you for registering. Please verify your email before continuing."
        }
    
1. User login
- /api/auth/login/
- post
- required_fields
    - emial
    - password
- response

        HTTP 200 OK
        Allow: POST, OPTIONS
        Content-Type: application/json
        Vary: Accept
        
        {
            "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluQGdtYWlsLmNvbSIsImV4cCI6MTUyNzY0OTY0NCwiZW1haWwiOiJhZG1pbkBnbWFpbC5jb20iLCJvcmlnX2lhdCI6MTUyNzY0OTM0NH0.L3chAa0WAQIN7TjaXWCH3MujTuo3ud38rtO_Si3lsdc",
            "user": "admin@gmail.com",
            "expires": "2018-06-06T10:59:04.502241"
        }
    
2. Check/Search/Ordering all public projects list & Create new project
- /api/projects/
- /api/projects/?ordering=ordering_item&q=search_item
    - search_fields = ('project_type', 'founder__email')
    - ordering_fields = ('project_type', 'timestamp')
- get
    - check/search/ordering all public projects list
    - response
    
            HTTP 200 OK
            Allow: GET, POST, HEAD, OPTIONS
            Content-Type: application/json
            Vary: Accept
            
            {
                "count": 2,
                "next": null,
                "previous": null,
                "results": [
                    {
                        "id": 1,
                        "project_type": "TextClassification",
                        "founder": 1,
                        "contributors": [
                            1,
                            2,
                            3,
                            4
                        ],
                        "description": "temp_description",
                        "private": false,
                        "deadline": null,
                        "project_file": "http://127.0.0.1:8000/media/3smbdat7cb.zip",
                        "uri": "http://127.0.0.1:8000/api/projects/1/"
                    },
                    {
                        "id": 3,
                        "project_type": "TextClassification",
                        "founder": 1,
                        "contributors": [
                            1,
                            2,
                            3,
                            4
                        ],
                        "description": "another_description",
                        "private": false,
                        "deadline": "2018-05-31T14:34:00",
                        "project_file": "http://127.0.0.1:8000/media/qnn1xltp64.zip",
                        "uri": "http://127.0.0.1:8000/api/projects/3/"
                    }
                ]
            }
- post
    - create new project
    - required fields
        - project_type
        - contributors
        - description
        - deadline
        - project_file
    - response
    
            HTTP 201 Created
            Allow: GET, POST, HEAD, OPTIONS
            Content-Type: application/json
            Vary: Accept
            
            {
                "id": 3,
                "project_type": "TextClassification",
                "founder": 1,
                "contributors": [
                    1,
                    2,
                    3,
                    4
                ],
                "description": "another_description",
                "private": false,
                "deadline": "2018-05-31T14:34:00",
                "project_file": "http://127.0.0.1:8000/media/qnn1xltp64.zip",
                "uri": "http://127.0.0.1:8000/api/projects/3/"

2. Staff get all pending verifying projects & verify particular project
- api/projects/verify/
- search/ordering
    - search_fields = ('project_type', 'founder__email')
    - ordering_fields = ('project_type', 'timestamp')
- get

- /api/projects/3/verify/
- put
- response

        HTTP 200 OK
        Allow: GET, PUT, PATCH, HEAD, OPTIONS
        Content-Type: application/json
        Vary: Accept
        
        {
            "id": 3,
            "project_type": "TextClassification",
            "founder": 1,
            "description": "another_description",
            "verify_status": "verification succeed",
            "project_file": "http://127.0.0.1:8000/media/qnn1xltp64.zip",
            "uri": "http://127.0.0.1:8000/api/projects/3/"
        }

3. Check all the contributors of a particular project & Users participate/quit the projects they want
- api/projects/(?P<id>\d+)/contributors/
- get 
    - response
    
            HTTP 200 OK
            Allow: GET, PUT, HEAD, OPTIONS
            Content-Type: application/json
            Vary: Accept
            
            {
                "count": 4,
                "next": null,
                "previous": null,
                "results": [
                    {
                        "id": 1,
                        "email": "admin@gmail.com",
                        "uri": "http://127.0.0.1:8000/api/users/1/"
                    },
                    {
                        "id": 2,
                        "email": "eli@gmail.com",
                        "uri": "http://127.0.0.1:8000/api/users/2/"
                    },
                    {
                        "id": 3,
                        "email": "django@gmail.com",
                        "uri": "http://127.0.0.1:8000/api/users/3/"
                    },
                    {
                        "id": 4,
                        "email": "tree@gmail.com",
                        "uri": "http://127.0.0.1:8000/api/users/4/"
                    }
                ]
            }
                            
- put
    - participate/quit project
    
    
4. Contributors annotate the task
- api/tasks/(?P<id>\d+)/
- get
    - get one spare unlabeled item
    - response 
    
            HTTP 200 OK
            Allow: GET, PUT, PATCH, HEAD, OPTIONS
            Content-Type: application/json
            Vary: Accept
            
            {
                "id": 2,
                "project": 1,
                "file_path": "/Users/eli/Projects/annotation/media_root/tw57azuamg/a/a.txt",
                "label": "",
                "contributor": null
            }
- put
    - annotate one item
    - response
    
            HTTP 200 OK
            Allow: GET, PUT, PATCH, HEAD, OPTIONS
            Content-Type: application/json
            Vary: Accept
            
            {
                "id": 1,
                "project": 1,
                "file_path": "/Users/eli/Projects/annotation/media_root/tw57azuamg/a/b.txt",
                "label": "oh",
                "contributor": 1
            }