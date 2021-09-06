function checkAll(bx) {
    var cbs = bx.parentNode.parentNode.querySelectorAll('input[type="checkbox"]');
    for (var i = 0; i < cbs.length; i++) {
        if (cbs[i].type == 'checkbox') {
            cbs[i].checked = bx.checked;
        }
    }
}
