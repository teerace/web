String.prototype.format = function () {
    var formatted = this;
    for (arg in arguments) {
        formatted = formatted.replace ("{" + arg + "}", arguments[arg]);
    }
    return formatted;
};