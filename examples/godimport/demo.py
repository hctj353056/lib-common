"""
godimport 使用示例
通用编程语言调用兼容模块
"""
import sys
sys.path.insert(0, 'src')

from godimport import import_plugin


def main():
    plugins_dir = "examples/godimport/plugins"
    
    print("=== godimport 示例 ===\n")
    
    # Python 插件
    print("1. Python 插件:")
    py = import_plugin(f"{plugins_dir}/calc.py")
    print(f"   run() -> {py.run()}")
    print(f"   add(1, 2) -> {py.call('add', 1, 2)}")
    print(f"   greet('World') -> {py.call('greet', 'World')}")
    print()
    
    # JavaScript 插件
    print("2. JavaScript 插件:")
    js = import_plugin(f"{plugins_dir}/math.js")
    print(f"   run() -> {js.run()}")
    print(f"   multiply(3, 4) -> {js.call('multiply', 3, 4)}")
    print(f"   greet('JS') -> {js.call('greet', 'JS')}")
    print()
    
    # Lua 插件
    print("3. Lua 插件:")
    lua = import_plugin(f"{plugins_dir}/utils.lua")
    print(f"   run() -> {lua.run()}")
    print(f"   add(5, 6) -> {lua.call('add', 5, 6)}")
    print(f"   greet('Lua') -> {lua.call('greet', 'Lua')}")
    print()
    
    # Bash 插件
    print("4. Bash 插件:")
    sh = import_plugin(f"{plugins_dir}/hello.sh")
    print(f"   run() -> {sh.run()}")


if __name__ == "__main__":
    main()
