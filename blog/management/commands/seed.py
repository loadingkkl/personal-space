import os
import random
import urllib.request
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from PIL import Image, ImageDraw, ImageFont

from blog.models import Post


COVER_PALETTES = [
    [(79, 70, 229), (129, 140, 248)],
    [(14, 165, 233), (56, 189, 248)],
    [(16, 185, 129), (52, 211, 153)],
    [(245, 158, 11), (251, 191, 36)],
    [(239, 68, 68), (248, 113, 113)],
    [(168, 85, 247), (192, 132, 252)],
    [(236, 72, 153), (244, 114, 182)],
    [(20, 184, 166), (94, 234, 212)],
    [(99, 102, 241), (165, 180, 252)],
    [(234, 88, 12), (251, 146, 60)],
    [(30, 64, 175), (96, 165, 250)],
    [(5, 150, 105), (110, 231, 183)],
    [(190, 18, 60), (251, 113, 133)],
    [(109, 40, 217), (167, 139, 250)],
    [(202, 138, 4), (250, 204, 21)],
    [(15, 118, 110), (45, 212, 191)],
    [(185, 28, 28), (252, 165, 165)],
    [(67, 56, 202), (139, 92, 246)],
    [(4, 120, 87), (52, 211, 153)],
    [(217, 70, 239), (232, 121, 249)],
]


def generate_cover(title, index, width=960, height=480):
    """Use Pillow to generate a gradient cover image with title text."""
    c1, c2 = COVER_PALETTES[index % len(COVER_PALETTES)]
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    for y in range(height):
        r = int(c1[0] + (c2[0] - c1[0]) * y / height)
        g = int(c1[1] + (c2[1] - c1[1]) * y / height)
        b = int(c1[2] + (c2[2] - c1[2]) * y / height)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # decorative circles
    for _ in range(6):
        cx = random.randint(0, width)
        cy = random.randint(0, height)
        cr = random.randint(40, 160)
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(255, 255, 255, 25))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')

    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("msyh.ttc", 40)
    except (OSError, IOError):
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except (OSError, IOError):
            font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), title, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = (width - tw) // 2
    ty = (height - th) // 2
    draw.text((tx + 2, ty + 2), title, font=font, fill=(0, 0, 0, 80))
    draw.text((tx, ty), title, font=font, fill=(255, 255, 255))

    buf = BytesIO()
    img.save(buf, format='JPEG', quality=88)
    return buf.getvalue()


def download_image(url, timeout=8):
    """Try downloading an image from a URL."""
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


PICSUM_IDS = [
    29, 37, 39, 47, 59, 65, 76, 84, 96, 100,
    106, 110, 119, 137, 142, 155, 164, 169, 180, 193,
]


class Command(BaseCommand):
    help = '生成示例博客数据（含20篇带封面图的文章）'

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={'is_staff': True, 'is_superuser': True},
        )
        if created or not user.has_usable_password():
            user.set_password('admin')
            user.save()

        Post.objects.all().delete()
        posts_data = [
            {
                'title': 'Django 入门：从零搭建个人博客',
                'excerpt': '手把手教你使用 Django 框架搭建一个功能完整的个人博客网站，涵盖模型设计、视图编写和模板渲染。',
                'body': 'Django 是 Python 最流行的 Web 框架之一，以其"开箱即用"的设计理念著称。\n\n本文将带你从零开始，一步步搭建一个具有文章管理、分类标签、评论功能的个人博客。\n\n首先，我们需要了解 Django 的 MTV（Model-Template-View）架构模式：\n\n- Model：定义数据结构和数据库操作\n- Template：负责页面展示\n- View：处理业务逻辑，连接 Model 和 Template\n\nDjango 的 ORM 让数据库操作变得简单直观，你只需定义 Python 类，Django 就会自动为你创建数据库表。通过内置的 Admin 后台，你可以方便地管理数据内容。\n\n路由系统使用 URLconf 配置，将 URL 映射到视图函数或类视图。模板引擎支持继承和组件化，让你轻松构建一致的页面布局。',
                'category': 'Python', 'tags': ['Django', 'Git'], 'featured': True,
            },
            {
                'title': 'Python 异步编程完全指南',
                'excerpt': '深入理解 Python 的 asyncio 模块，掌握协程、事件循环和异步 I/O 的核心概念。',
                'body': '随着 Web 应用对并发性能要求越来越高，异步编程成为 Python 开发者的必备技能。\n\nPython 从 3.5 版本开始引入了 async/await 语法，让异步代码的编写变得优雅简洁。\n\n核心概念：\n1. 协程（Coroutine）：使用 async def 定义的函数\n2. 事件循环（Event Loop）：调度和执行协程的核心引擎\n3. 任务（Task）：对协程的包装，可以并发执行\n\nasyncio 最常见的使用场景包括网络 I/O、文件操作和数据库查询等。通过异步编程，我们可以在等待 I/O 操作完成的同时处理其他任务，大幅提升程序性能。',
                'category': 'Python', 'tags': ['Flask', 'FastAPI'], 'featured': True,
            },
            {
                'title': 'Vue 3 组合式 API 实战技巧',
                'excerpt': '探索 Vue 3 Composition API 的强大功能，学习如何编写更加可复用和可维护的组件。',
                'body': 'Vue 3 引入的组合式 API（Composition API）为组件逻辑的组织和复用提供了全新方式。\n\n相比 Options API，Composition API 允许我们按功能而非选项类型来组织代码，使得相关逻辑更加内聚。\n\n关键特性包括 ref 和 reactive 创建响应式数据、computed 计算属性、watch 和 watchEffect 侦听数据变化。\n\n通过自定义组合函数（Composables），我们可以将组件逻辑提取为可复用的函数，在不同组件之间共享状态和行为。',
                'category': '前端开发', 'tags': ['JavaScript', 'Vue', 'CSS'], 'featured': True,
            },
            {
                'title': 'Docker 容器化部署最佳实践',
                'excerpt': '从 Dockerfile 编写到多阶段构建，全面掌握 Docker 在生产环境中的部署技巧。',
                'body': 'Docker 已经成为现代应用部署的标准工具。本文分享经过实战验证的 Docker 最佳实践：\n\n1. 使用多阶段构建减小镜像体积\n2. 合理利用构建缓存加速构建过程\n3. 使用 .dockerignore 排除不需要的文件\n4. 以非 root 用户运行容器\n5. 使用健康检查确保服务可用\n\n在生产环境中，建议使用 docker-compose 或 Kubernetes 来编排多个容器服务，同时配合 CI/CD 流水线实现自动化部署。',
                'category': 'DevOps', 'tags': ['Docker', 'Linux', 'Kubernetes'], 'featured': True,
            },
            {
                'title': 'PostgreSQL 性能优化实战',
                'excerpt': '深入了解 PostgreSQL 的查询优化器、索引策略和配置调优，提升数据库查询性能。',
                'body': '数据库性能优化是后端开发中的关键环节。PostgreSQL 提供了丰富的优化手段：\n\n1. EXPLAIN ANALYZE：分析查询执行计划\n2. 合理创建索引：B-Tree、GiST、GIN 等索引类型\n3. 分区表：对大表进行水平分区\n4. 连接池：使用 PgBouncer 减少连接开销\n5. 配置优化：shared_buffers、work_mem 等参数调优\n\n使用 pg_stat_statements 扩展可以帮助你找到最耗时的查询，然后有针对性地进行优化。',
                'category': '数据库', 'tags': ['PostgreSQL', 'Redis'], 'featured': True,
            },
            {
                'title': '程序员的自我修养：持续学习之道',
                'excerpt': '分享作为程序员如何保持学习热情、建立知识体系、平衡工作与生活的心得。',
                'body': '技术世界日新月异，作为程序员，持续学习不是选择而是必然。\n\n1. 建立知识体系：不要追求面面俱到，而是在一个领域深入后再横向扩展\n2. 实践驱动学习：最好的学习方式是做项目\n3. 写技术博客：输出是最好的学习方式\n4. 参与开源：阅读优秀的开源代码\n5. 保持好奇心：对新技术保持开放态度\n\n最重要的是不要忘记生活。保持运动、阅读、社交，这些都能让你成为更好的程序员。',
                'category': '生活随笔', 'tags': ['Git'],
            },
            {
                'title': 'FastAPI：高性能 Python Web 框架',
                'excerpt': 'FastAPI 凭借类型提示和异步支持，成为构建高性能 API 的首选框架。',
                'body': 'FastAPI 是一个现代、快速的 Python Web 框架，基于标准 Python 类型提示构建。\n\n它的主要优势包括：\n- 极高的性能，可与 Node.js 和 Go 媲美\n- 自动生成交互式 API 文档（Swagger UI 和 ReDoc）\n- 基于 Pydantic 的数据验证\n- 原生支持异步编程\n- 依赖注入系统\n\nFastAPI 特别适合构建微服务架构中的 API 服务。配合 Uvicorn ASGI 服务器，可以充分利用异步特性处理高并发请求。',
                'category': 'Python', 'tags': ['FastAPI', 'REST API'],
            },
            {
                'title': 'React Hooks 深度解析',
                'excerpt': '全面理解 React Hooks 的工作原理，掌握 useState、useEffect、useContext 等核心 Hook。',
                'body': 'React Hooks 从 16.8 版本引入，彻底改变了 React 组件的编写方式。\n\n核心 Hooks：\n- useState：管理组件状态\n- useEffect：处理副作用\n- useContext：消费 Context\n- useReducer：复杂状态管理\n- useMemo / useCallback：性能优化\n- useRef：引用 DOM 或保存可变值\n\n自定义 Hook 是 React 中最强大的代码复用模式。通过提取公共逻辑到自定义 Hook，你可以在不同组件间共享状态逻辑，同时保持组件的简洁。',
                'category': '前端开发', 'tags': ['JavaScript', 'React', 'TypeScript'],
            },
            {
                'title': 'Kubernetes 集群搭建与管理',
                'excerpt': '从 K8s 基础概念到生产级集群搭建，全面掌握容器编排技术。',
                'body': 'Kubernetes（K8s）是容器编排的事实标准。\n\n核心概念：\n- Pod：最小调度单元\n- Deployment：管理 Pod 的声明式更新\n- Service：为 Pod 提供稳定的网络访问\n- Ingress：管理外部访问\n- ConfigMap / Secret：配置管理\n- PersistentVolume：持久化存储\n\n搭建生产级集群需要考虑高可用、网络方案（如 Calico、Flannel）、存储方案、监控告警（Prometheus + Grafana）以及日志收集（ELK Stack）等方面。',
                'category': 'DevOps', 'tags': ['Kubernetes', 'Docker', 'Linux'],
            },
            {
                'title': 'Redis 缓存设计模式',
                'excerpt': '深入探讨 Redis 在实际项目中的缓存策略，解决缓存穿透、击穿和雪崩问题。',
                'body': 'Redis 是最流行的内存数据库，广泛用于缓存、会话管理、排行榜等场景。\n\n常见缓存模式：\n- Cache Aside：先查缓存，未命中再查数据库\n- Read/Write Through：缓存作为主要数据源\n- Write Behind：异步写入数据库\n\n缓存问题及解决方案：\n- 缓存穿透：布隆过滤器 + 空值缓存\n- 缓存击穿：互斥锁 + 热点数据永不过期\n- 缓存雪崩：随机过期时间 + 多级缓存\n\nRedis 还支持发布订阅、Lua 脚本、Stream 等高级特性。',
                'category': '数据库', 'tags': ['Redis', 'Django'],
            },
            {
                'title': 'TypeScript 进阶：类型体操指南',
                'excerpt': '掌握 TypeScript 高级类型技巧，包括泛型、条件类型、映射类型和类型推断。',
                'body': 'TypeScript 的类型系统是图灵完备的，这意味着你可以用类型来表达几乎任何逻辑。\n\n高级类型技巧：\n- 泛型约束：extends 关键字限制类型参数\n- 条件类型：T extends U ? X : Y\n- 映射类型：将已有类型转换为新类型\n- 模板字面量类型：类型级别的字符串操作\n- infer 关键字：在条件类型中推断类型\n\n实用工具类型：Partial、Required、Pick、Omit、Record 等内置工具类型覆盖了大部分常见场景。',
                'category': '前端开发', 'tags': ['TypeScript', 'JavaScript'],
            },
            {
                'title': '深度学习入门：从神经网络到 Transformer',
                'excerpt': '循序渐进地理解深度学习核心概念，从基础神经网络到当今最火的 Transformer 架构。',
                'body': '深度学习是人工智能领域最重要的技术分支。\n\n学习路径：\n1. 感知机与多层网络：理解前向传播和反向传播\n2. 卷积神经网络（CNN）：图像识别的基石\n3. 循环神经网络（RNN/LSTM）：序列数据处理\n4. 注意力机制：让模型学会"关注"重要信息\n5. Transformer：自注意力机制的革命性架构\n6. GPT / BERT：预训练大语言模型\n\n推荐使用 PyTorch 或 TensorFlow 框架入门，先从小项目做起，逐步深入理论。',
                'category': '人工智能', 'tags': ['REST API'],
            },
            {
                'title': 'Nginx 从入门到精通',
                'excerpt': '全面解析 Nginx 的反向代理、负载均衡、HTTPS 配置和性能调优。',
                'body': 'Nginx 是全球最流行的 Web 服务器和反向代理服务器。\n\n核心功能：\n- 静态文件服务：高效的文件传输\n- 反向代理：将请求转发到后端服务\n- 负载均衡：轮询、权重、IP Hash 等策略\n- HTTPS：Let\'s Encrypt 免费证书配置\n- Gzip 压缩：减少传输数据量\n- 缓存：代理缓存和浏览器缓存\n\n性能调优要点包括 worker_processes、worker_connections 配置，以及 keepalive、buffer 相关参数的合理设置。',
                'category': 'DevOps', 'tags': ['Nginx', 'Linux', 'Docker'],
            },
            {
                'title': 'MySQL 高可用架构方案对比',
                'excerpt': '对比 MySQL 主从复制、MGR、Galera Cluster 等高可用方案的优缺点。',
                'body': 'MySQL 高可用是生产环境的基本需求。\n\n常见方案对比：\n\n1. 主从复制 + MHA\n- 优点：架构简单，部署容易\n- 缺点：数据可能丢失，故障切换需要工具\n\n2. MySQL Group Replication (MGR)\n- 优点：官方方案，支持多主\n- 缺点：对网络要求高\n\n3. Galera Cluster\n- 优点：同步复制，数据强一致\n- 缺点：写性能受限于最慢节点\n\n4. InnoDB Cluster\n- 优点：官方完整解决方案\n- 缺点：组件较多，运维复杂\n\n选择方案时需综合考虑数据一致性要求、性能需求和运维能力。',
                'category': '数据库', 'tags': ['MySQL', 'Docker'],
            },
            {
                'title': 'Flutter 跨平台开发实战',
                'excerpt': '使用 Flutter 构建高性能的 iOS 和 Android 应用，一套代码多端运行。',
                'body': 'Flutter 是 Google 推出的跨平台 UI 框架，使用 Dart 语言开发。\n\n核心优势：\n- 一套代码同时运行在 iOS、Android、Web 和桌面\n- 自绘引擎，UI 一致性极高\n- Hot Reload，开发体验优秀\n- 丰富的 Material 和 Cupertino 组件库\n\n架构设计：\n- 使用 Provider 或 Riverpod 进行状态管理\n- 使用 Go Router 处理导航路由\n- 使用 Dio 进行网络请求\n- 使用 Hive 或 SQLite 做本地存储\n\nFlutter 正在快速发展，社区生态也越来越成熟。',
                'category': '移动开发', 'tags': ['CSS', 'JavaScript'],
            },
            {
                'title': 'GraphQL vs REST：API 设计之争',
                'excerpt': '深入对比 GraphQL 和 REST API 的优劣势，帮助你在项目中做出正确选择。',
                'body': 'GraphQL 和 REST 是两种主流的 API 设计风格。\n\nREST 的优势：\n- 简单直观，学习成本低\n- HTTP 缓存友好\n- 生态成熟，工具丰富\n\nGraphQL 的优势：\n- 客户端按需获取数据\n- 强类型 Schema\n- 单一端点，减少请求次数\n- 自带文档（Introspection）\n\n选择建议：\n- 简单 CRUD 应用：REST 足够\n- 多客户端、复杂数据关系：GraphQL 更合适\n- 微服务网关聚合：GraphQL 是理想选择\n\n两者并非互斥，很多项目会混合使用。',
                'category': '架构设计', 'tags': ['GraphQL', 'REST API'],
            },
            {
                'title': 'CI/CD 流水线设计与实践',
                'excerpt': '基于 GitHub Actions 和 Jenkins 构建完整的持续集成与持续部署流水线。',
                'body': 'CI/CD 是现代软件交付的核心实践。\n\n流水线阶段：\n1. 代码检查：Lint、格式化\n2. 单元测试：确保代码质量\n3. 构建：编译、打包\n4. 集成测试：端到端测试\n5. 部署：自动发布到各环境\n\nGitHub Actions 示例：\n- 代码推送触发自动测试\n- PR 合并后自动部署到预发环境\n- Tag 发布触发生产部署\n\n最佳实践包括快速反馈、环境一致性、回滚机制、渐进式发布（蓝绿/金丝雀）等。',
                'category': 'DevOps', 'tags': ['CI/CD', 'Docker', 'Git'],
            },
            {
                'title': 'MongoDB 文档数据库设计指南',
                'excerpt': '掌握 MongoDB 的数据建模、索引策略和聚合管道，充分发挥文档数据库的优势。',
                'body': 'MongoDB 是最流行的 NoSQL 文档数据库。\n\n数据建模原则：\n- 内嵌 vs 引用：一对少用内嵌，一对多用引用\n- 读写比例决定模型设计\n- 避免无限增长的数组\n\n索引优化：\n- 复合索引遵循 ESR 原则（等值、排序、范围）\n- 覆盖索引减少磁盘 I/O\n- 使用 explain() 分析查询\n\n聚合管道是 MongoDB 最强大的数据处理工具，$match、$group、$lookup、$project 等阶段可以组合完成复杂的数据分析。',
                'category': '数据库', 'tags': ['MongoDB', 'REST API'],
            },
            {
                'title': '微服务架构设计原则',
                'excerpt': '探讨微服务拆分策略、服务治理、数据一致性和分布式事务的最佳实践。',
                'body': '微服务架构将单体应用拆分为多个小型、独立部署的服务。\n\n设计原则：\n1. 单一职责：每个服务只做一件事\n2. 自治性：服务独立开发、部署、扩展\n3. 去中心化：避免共享数据库\n4. 容错设计：熔断、降级、限流\n\n关键技术栈：\n- 服务发现：Consul、Nacos\n- 配置中心：Apollo、Spring Cloud Config\n- API 网关：Kong、APISIX\n- 链路追踪：Jaeger、Zipkin\n- 消息队列：Kafka、RabbitMQ\n\n微服务不是银弹，小团队和简单项目可能更适合单体架构。',
                'category': '架构设计', 'tags': ['Docker', 'Kubernetes', 'REST API'],
            },
            {
                'title': '大语言模型应用开发实战',
                'excerpt': '基于 LLM API 构建智能应用，掌握 Prompt Engineering 和 RAG 技术。',
                'body': '大语言模型（LLM）正在改变软件开发的方式。\n\n应用开发关键技术：\n\n1. Prompt Engineering\n- 角色设定：给模型明确的身份\n- 少样本学习：提供示例引导输出\n- 思维链：让模型逐步推理\n\n2. RAG（检索增强生成）\n- 文档向量化：将知识库转为向量\n- 语义检索：找到最相关的上下文\n- 增强生成：结合检索结果回答问题\n\n3. Agent 开发\n- 工具调用：让 LLM 使用外部工具\n- 任务规划：自动分解复杂任务\n- 记忆机制：长期和短期记忆管理\n\n推荐框架：LangChain、LlamaIndex。',
                'category': '人工智能', 'tags': ['FastAPI', 'REST API'],
            },
        ]

        self.stdout.write('\n正在创建文章并下载封面图...')
        for i, data in enumerate(posts_data):
            post = Post.objects.create(
                title=data['title'],
                body=data['body'],
                excerpt=data['excerpt'],
                category_name=data['category'],
                tag_names=', '.join(data['tags']),
                author=user,
                views=random.randint(50, 2000),
                is_featured=data.get('featured', False),
            )
            img_data = None
            pid = PICSUM_IDS[i % len(PICSUM_IDS)]
            url = f'https://picsum.photos/id/{pid}/960/480'
            try:
                img_data = download_image(url, timeout=15)
            except Exception:
                pass

            if not img_data:
                img_data = generate_cover(data['title'], i)

            filename = f'cover_{i+1:02d}.jpg'
            post.cover.save(filename, ContentFile(img_data), save=True)
            self.stdout.write(self.style.SUCCESS(f'  [{i+1:2d}/20] {post.title}'))

        total = Post.objects.count()
        featured = Post.objects.filter(is_featured=True).count()
        self.stdout.write(self.style.SUCCESS(f'\n完成！共 {total} 篇文章，其中 {featured} 篇为轮播推荐'))
        self.stdout.write(self.style.WARNING(
            '\n管理员账号: admin / admin'
            '\n访问 http://127.0.0.1:8000 查看博客'
            '\n访问 http://127.0.0.1:8000/admin/ 进入后台'
        ))
