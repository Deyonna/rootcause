$(document).ready(function () {
    const $toolbar = $('#md-toolbar');
    const $textarea = $('#id_body');
    if (!$toolbar.length || !$textarea.length) return;

    const textarea = $textarea.get(0);

    function wrapSelection(before, after) {
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const selected = textarea.value.slice(start, end) || 'text';
        const replacement = before + selected + (after === undefined ? before : after);
        textarea.setRangeText(replacement, start, end, 'select');
        $textarea.focus();
    }

    function prefixLine(prefix) {
        const start = textarea.selectionStart;
        const lineStart = textarea.value.lastIndexOf('\n', start - 1) + 1;
        textarea.setRangeText(prefix, lineStart, lineStart, 'end');
        $textarea.focus();
    }

    const actions = {
        bold: () => wrapSelection('**'),
        italic: () => wrapSelection('*'),
        code: () => wrapSelection('`'),
        codeblock: () => wrapSelection('\n```\n', '\n```\n'),
        heading: () => prefixLine('## '),
        list: () => prefixLine('- '),
        link: () => wrapSelection('[', '](https://)'),
    };

    $toolbar.find('[data-md]').on('click', function (event) {
        event.preventDefault();
        const action = actions[$(this).data('md')];
        if (action) action();
    });
});
