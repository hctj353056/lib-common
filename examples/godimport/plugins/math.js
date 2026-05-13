/**
 * JavaScript 插件示例
 */

function multiply(a, b) {
    return a * b;
}

function greet(name) {
    return `Hello from JS, ${name}!`;
}

function run() {
    return "JavaScript plugin loaded!";
}

module.exports = {
    multiply,
    greet,
    run
};
