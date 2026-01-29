---
description: 本项目严格遵循 Google C++ 开源项目风格指南
---

### 核心命名规范 (Naming Conventions)

* **类与结构体**: 使用 **PascalCase**。例如：`class TimeTracer;`
* **函数与方法**: 使用 **PascalCase**。示例：`void StartTimer();`
* **变量**:
* **局部变量**: 使用 **snake_case**（全小写，单词间加下划线）。例如：`local_variable`
* **类成员变量**: 小写加**后缀下划线**。例如：`int task_id_;`


* **常量与枚举值**: 以小写 `k` 开头，后接大写字母（PascalCase）。例如：`const int kMaxRetryCount = 3;` 或 `enum { kStateRunning };`
* **宏**: 全大写加下划线。例如：`#define MY_MACRO_VALUE`

### 编程工程规范 (Engineering Best Practices)

* **构造函数 (Explicit Constructors)**
* **规则**: 所有单参数构造函数必须声明为 `explicit`。
* **目的**: 防止编译器进行隐式类型转换，避免难以察觉的逻辑错误。


* **虚函数标记 (Virtual Functions)**
* **规则**: 在子类重写父类虚函数时，必须明确使用 `override` 关键字。
* **目的**: 确保重写行为符合预期，若父类签名改变，编译器能立即发现错误。


* **输出参数规范 (Output Parameters)**
* **规则**: 尽量避免使用非常量引用（`T&`）作为输出参数。如果函数需要修改参数值，建议使用指针（`T*`）。
* **目的**: 在调用处通过 `&variable` 能够直观识别该变量会被修改，提升代码可读性。

* **全局变量限制 (Global Variables)**
* **规则**: 禁止使用具有复杂初始化逻辑的全局变量。
* **目的**: 消除“全局初始化顺序陷阱”（Static Initialization Order Fiasco），确保程序启动的稳定性。

### 代码格式与结构 (Formatting)

* **包含规范 (Include Rules)**
* **禁止使用相对路径**: 严禁在 `#include` 中使用 `..`（父目录）导航。
* **绝对路径引用**: 所有项目内头文件必须从 `src/` 根目录开始引用。
* *正确*: `#include "domain/services/time_tracer.h"`
* *错误*: `#include "../services/time_tracer.h"`
* **头文件包含顺序**
按照“相关头文件（.h对应的.cpp文件优先）、C 系统库、C++ 标准库、其他第三方库、本项目内的 .h”排序，各组之间空行。
* **头文件卫士 (Include Guards)**
使用格式 `#ifndef PATH_FILE_H_`（基于项目根目录）。



