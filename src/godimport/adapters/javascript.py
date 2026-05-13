"""
JavaScript 适配器
"""
import os
import shutil
import tempfile
from pathlib import Path

from ..base import Plugin


# JS 通信桥脚本（内嵌）
JS_BRIDGE = """
const fs = require('fs');
const path = require('path');

// 绝对路径
const pluginPath = path.resolve(process.argv[2]);
const pluginDir = path.dirname(pluginPath);

// 读取输入
let input = '';
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
    try {
        const payload = JSON.parse(input);
        let result;
        let error = null;
        
        // 设置模块搜索路径
        module.paths.unshift(pluginDir);
        
        // 加载插件
        const plugin = require(pluginPath);
        
        switch (payload.action) {
            case 'run':
                result = typeof plugin.run === 'function' 
                    ? plugin.run() 
                    : plugin;
                break;
            case 'call':
                const fn = plugin[payload.function];
                if (typeof fn === 'function') {
                    result = fn.apply(null, [...payload.args, payload.kwargs || {}]);
                } else {
                    error = `Function '${payload.function}' not found`;
                }
                break;
            case 'eval':
                result = eval(payload.code);
                break;
            default:
                error = `Unknown action: ${payload.action}`;
        }
        
        console.log(JSON.stringify({ result, error }));
    } catch (e) {
        console.log(JSON.stringify({ result: null, error: e.message }));
    }
});
"""


class JavaScriptPlugin(Plugin):
    """
    JavaScript 插件适配器
    
    需要 Node.js 环境
    被加载的 JS 文件需要导出 run() 或其他函数
    """
    
    EXTENSIONS = ('.js', '.mjs')
    INTERPRETER = 'node'
    
    def __init__(self, path):
        super().__init__(path)
        # 检查 node 是否可用
        if not shutil.which('node'):
            raise EnvironmentError("Node.js is not installed")
    
    def build_command(self):
        # 生成临时桥接脚本
        bridge_path = Path(tempfile.gettempdir()) / f"godimport_js_{os.getpid()}.js"
        Path(bridge_path).write_text(JS_BRIDGE)
        return ['node', str(bridge_path), str(self.path.resolve())]
