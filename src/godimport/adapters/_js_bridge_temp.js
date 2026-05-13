
const fs = require('fs');
const path = require('path');

// 接收插件路径
const pluginPath = process.argv[2];
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
        if (!global.module_paths) global.module_paths = [];
        global.module_paths.push(pluginDir);
        
        // 加载插件
        const plugin = require(pluginPath);
        
        switch (payload.action) {
            case 'run':
                result = typeof plugin.run === 'function' 
                    ? plugin.run() 
                    : plugin;
                break;
            case 'call':
                if (typeof plugin[payload.function] === 'function') {
                    result = plugin[payload.function](
                        ...payload.args,
                        ...payload.kwargs
                    );
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
