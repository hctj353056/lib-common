#!/bin/bash
# Bash 插件示例

# 读取输入 JSON
INPUT_FILE="$GODIMPORT_INPUT"
if [ -z "$INPUT_FILE" ] && [ ! -t 0 ]; then
    INPUT=$(cat)
else
    INPUT='{"action":"run"}'
fi

# 简单的命令处理
case "$1" in
    add)
        echo $(( $2 + $3 ))
        ;;
    *)
        echo '{"result":"Bash plugin loaded!","error":null}'
        ;;
esac
