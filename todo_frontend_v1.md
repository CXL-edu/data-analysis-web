我要做AI数据分析助手的前端界面，用户上传电子表格，后端进行分析，前端可以流式的将分析结果展示，将图片渲染到界面。

我的初步想法是：
左侧侧边栏（包含收起按钮）：从上到下依次是，新建聊天按钮，知识库按钮，历史聊天记录，最下方显示用户登录信息（包含头像和名称）
中间对话区（主区域，最大的区域）：类似聊天窗口，用于展示AI和用户的对话，对话部分要展示用户头像和AI的icon，下方放置输入框
右侧实时预览区（当开始分析，触发预览条件后才弹出展示，未触发条件时是收起态）：当接受到用户上传的数据，将数据的前5行展示在这个区域，当数据被处理后更新这个预览表格，当有图像被绘制时，展示在这个区域。这个区域同样包含收起按钮。这个区域只展示当前的数据状态，即预览前几行，当前的实时的处理情况，如果有新的图片进来会覆盖之前的图片

注意只是实现react前端，后端由后续的python实现。
要求以组件化的方式实现，相关组件放到app\components\product路径下，前端页面在app\(home)\product\page.tsx中修改。


可以参考这个结构：
```
components
 └─ product
     ├─ LayoutWrapper.tsx        # 三栏整体布局
     ├─ Sidebar/                 # 左侧侧边栏
     │   ├─ Sidebar.tsx          # 容器，组合下面子组件
     │   ├─ SidebarHeader.tsx    # 新建聊天按钮（可带Logo）
     │   ├─ SidebarNav.tsx       # 知识库按钮等
     │   ├─ SidebarHistory.tsx   # 历史聊天记录
     │   ├─ SidebarUserInfo.tsx  # 用户信息（头像+名称）
     │   └─ SidebarToggle.tsx    # 收起/展开按钮
     ├─ ChatArea/                # 中间对话区
     │   ├─ ChatArea.tsx         # 容器
     │   ├─ ChatMessage.tsx      # 单条消息（区分用户/AI）
     │   └─ ChatInput.tsx        # 输入框（含上传按钮）
     ├─ PreviewPanel/            # 右侧实时预览区
     │   ├─ PreviewPanel.tsx     # 容器，管理展开/收起
     │   ├─ DataPreviewTable.tsx # 表格展示前5行
     │   └─ ChartPreview.tsx     # 图像展示（覆盖旧图）
     └─ common/
         └─ Icon.tsx             # 公共图标封装
```