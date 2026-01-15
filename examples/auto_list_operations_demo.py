"""
演示 AutoList 的 Pythonic 列表操作

这个示例展示了如何像使用 Python 原生 list 一样使用 AutoList：
- 索引访问和切片
- 迭代和成员测试
- 追加、插入和扩展
- 删除和弹出元素
- 查找和计数
- 复制、反转和排序
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from hyperextract import AutoList

# 加载环境变量
load_dotenv()


# 定义一个简单的任务Schema
class Task(BaseModel):
    """项目任务"""

    name: str = Field(description="任务名称")
    priority: int = Field(description="优先级 (1-5)")
    status: str = Field(description="状态: pending, in_progress, done")


def main():
    # 初始化 LLM 和 Embedder
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
    )

    embedder = OpenAIEmbeddings(
        api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL")
    )

    # 创建 AutoList 实例
    a_task_list = AutoList(
        item_schema=Task,
        llm_client=llm,
        embedder=embedder,
    )

    print("=" * 70)
    print("AutoList Pythonic 操作演示")
    print("=" * 70)

    # 1. 使用 append 添加任务
    print("\n1. 使用 append() 添加任务:")
    a_task_list.append(Task(name="实现用户登录", priority=5, status="done"))
    a_task_list.append(Task(name="设计数据库", priority=4, status="done"))
    a_task_list.append(Task(name="编写API文档", priority=3, status="in_progress"))
    print(f"   已添加 {len(a_task_list)} 个任务")

    # 2. 索引访问
    print("\n2. 索引访问:")
    print(f"   第一个任务: {a_task_list[0].name} (优先级 {a_task_list[0].priority})")
    print(f"   最后一个任务: {a_task_list[-1].name} (状态: {a_task_list[-1].status})")

    # 3. 切片
    print("\n3. 切片操作:")
    high_priority = a_task_list[:2]
    print(f"   前两个高优先级任务:")
    for task in high_priority:
        print(f"     - {task.name} (P{task.priority})")

    # 4. 迭代
    print("\n4. 遍历所有任务:")
    for i, task in enumerate(a_task_list, 1):
        print(f"   {i}. {task.name} - {task.status}")

    # 5. 使用列表推导式
    print("\n5. 列表推导式 - 获取所有任务名称:")
    task_names = [task.name for task in a_task_list]
    print(f"   {task_names}")

    # 6. 成员测试
    print("\n6. 成员测试 (in 操作符):")
    test_task = Task(name="编写API文档", priority=3, status="in_progress")
    print(f"   测试任务在列表中: {test_task in a_task_list}")

    # 7. 插入任务
    print("\n7. 使用 insert() 在开头插入紧急任务:")
    a_task_list.insert(0, Task(name="修复生产BUG", priority=5, status="in_progress"))
    print(f"   新的第一个任务: {a_task_list[0].name}")

    # 8. 扩展多个任务
    print("\n8. 使用 extend() 批量添加任务:")
    new_tasks = [
        Task(name="代码审查", priority=3, status="pending"),
        Task(name="性能优化", priority=2, status="pending"),
    ]
    a_task_list.extend(new_tasks)
    print(f"   现在共有 {len(a_task_list)} 个任务")

    # 9. 查找和计数
    print("\n9. 查找和计数:")
    in_progress_count = sum(1 for t in a_task_list if t.status == "in_progress")
    print(f"   进行中的任务数量: {in_progress_count}")

    # 查找第一个 pending 任务的位置
    for i, task in enumerate(a_task_list):
        if task.status == "pending":
            print(f"   第一个待处理任务位置: 索引 {i} - {task.name}")
            break

    # 10. 修改任务
    print("\n10. 修改任务状态 (通过索引赋值):")
    print(f"   修改前: {a_task_list[-1].name} - {a_task_list[-1].status}")
    updated_task = a_task_list[-1]
    updated_task.status = "done"
    a_task_list[-1] = updated_task
    print(f"   修改后: {a_task_list[-1].name} - {a_task_list[-1].status}")

    # 11. 删除任务
    print("\n11. 删除已完成的任务:")
    print(f"   删除前共有 {len(a_task_list)} 个任务")
    # 删除第一个任务
    del a_task_list[0]
    print(f"   删除后共有 {len(a_task_list)} 个任务")

    # 12. Pop 操作
    print("\n12. 使用 pop() 移除并返回任务:")
    last_task = a_task_list.pop()
    print(f"   弹出的任务: {last_task.name}")
    print(f"   剩余 {len(a_task_list)} 个任务")

    # 13. 复制
    print("\n13. 创建任务列表的副本:")
    tasks_backup = a_task_list.copy()
    tasks_backup.append(Task(name="新任务", priority=1, status="pending"))
    print(f"   原始列表: {len(a_task_list)} 个任务")
    print(f"   副本列表: {len(tasks_backup)} 个任务")
    print("   ✓ 副本是独立的")

    # 14. 排序
    print("\n14. 按优先级排序任务 (降序):")
    a_task_list.sort(key=lambda t: t.priority, reverse=True)
    print("   排序后的任务列表:")
    for task in a_task_list:
        print(f"     - P{task.priority}: {task.name}")

    # 15. 反转
    print("\n15. 反转任务列表:")
    a_task_list.reverse()
    print("   反转后:")
    for task in a_task_list:
        print(f"     - {task.name}")

    # 16. 字符串表示
    print("\n16. 字符串表示:")
    print(f"   repr: {repr(a_task_list)}")
    print(f"   str: {str(a_task_list)}")

    # 17. 组合操作
    print("\n17. 组合两个 AutoList (+ 操作符):")
    more_tasks = AutoList(
        item_schema=Task,
        llm_client=llm,
        embedder=embedder,
    )
    more_tasks.append(Task(name="部署到生产", priority=5, status="pending"))

    combined = a_task_list + more_tasks
    print(f"   原始任务: {len(a_task_list)} 个")
    print(f"   新增任务: {len(more_tasks)} 个")
    print(f"   组合后: {len(combined)} 个")

    print("\n" + "=" * 70)
    print("✨ 所有 Pythonic 操作演示完成!")
    print("=" * 70)

    # 总结
    print("\n📝 主要特性总结:")
    print("   ✓ 索引访问: tasks[0], tasks[-1]")
    print("   ✓ 切片: tasks[1:3], tasks[:2]")
    print("   ✓ 迭代: for task in tasks")
    print("   ✓ 成员测试: task in tasks")
    print("   ✓ 修改方法: append, extend, insert, remove, pop")
    print("   ✓ 查询方法: index, count")
    print("   ✓ 工具方法: copy, reverse, sort")
    print("   ✓ 自动 schema 验证")
    print("   ✓ 语义搜索能力 (继承自基类)")


if __name__ == "__main__":
    main()
