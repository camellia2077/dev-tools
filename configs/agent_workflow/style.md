---
description: 本项目严格遵循 Google C++ 开源项目风格指南
---

### 核心命名规范 (Naming Conventions)

* **类与结构体**: 使用 **PascalCase**。
* **函数与方法**: 使用 **PascalCase**。

* **变量**:
* **局部变量**: 使用 **snake_case**（全小写，单词间加下划线）。例如：`local_variable`
* **类成员变量**: 小写加**后缀下划线**。例如：`int task_id_;`


* **常量与枚举值**: 以小写 `k` 开头，后接大写字母（PascalCase）。例如：`const int kMaxRetryCount = 3;` 或 `enum { kStateRunning };`
* **宏**: 全大写加下划线。例如：`#define MY_MACRO_VALUE`

### 编程工程规范 (Engineering Best Practices)

* **构造函数 (Explicit Constructors)**
* **规则**: 所有单参数构造函数必须声明为 `explicit`。

* **虚函数标记 (Virtual Functions)**
* **规则**: 在子类重写父类虚函数时，必须明确使用 `override` 关键字。

* **输出参数规范 (Output Parameters)**
* **规则**: 尽量避免使用非常量引用（`T&`）作为输出参数。如果函数需要修改参数值，建议使用指针（`T*`）。

* **全局变量限制 (Global Variables)**
* **规则**: 禁止使用具有复杂初始化逻辑的全局变量。

### 代码格式与结构 (Formatting)

* **包含规范 (Include Rules)**
* **禁止使用相对路径**: 严禁在 `#include` 中使用 `..`（父目录）导航。
* **绝对路径引用**: 所有项目内头文件必须从 `src/` 根目录开始引用。
