(function () {
    function escapeHtml(value) {
        return value
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function flushParagraph(lines, html) {
        if (!lines.length) return;
        html.push('<p>' + lines.map(escapeHtml).join('<br>') + '</p>');
        lines.length = 0;
    }

    function flushList(items, html) {
        if (!items.length) return;
        html.push('<ul>' + items.map(function (item) {
            return '<li>' + escapeHtml(item) + '</li>';
        }).join('') + '</ul>');
        items.length = 0;
    }

    function renderMarkdown(value) {
        var html = [];
        var paragraph = [];
        var list = [];

        value.split(/\r?\n/).forEach(function (rawLine) {
            var line = rawLine.trim();
            if (!line) {
                flushParagraph(paragraph, html);
                flushList(list, html);
                return;
            }

            if (line.indexOf('### ') === 0 && line.slice(4).trim()) {
                flushParagraph(paragraph, html);
                flushList(list, html);
                html.push('<h3>' + escapeHtml(line.slice(4).trim()) + '</h3>');
                return;
            }

            if (line.indexOf('## ') === 0 && line.slice(3).trim()) {
                flushParagraph(paragraph, html);
                flushList(list, html);
                html.push('<h2>' + escapeHtml(line.slice(3).trim()) + '</h2>');
                return;
            }

            if (line.indexOf('- ') === 0 && line.slice(2).trim()) {
                flushParagraph(paragraph, html);
                list.push(line.slice(2).trim());
                return;
            }

            flushList(list, html);
            paragraph.push(rawLine);
        });

        flushParagraph(paragraph, html);
        flushList(list, html);

        return html.join('') || '<p class="markdown-preview-empty">开始输入正文后，这里会显示预览。</p>';
    }

    function attachPreview(textarea) {
        var panel = document.createElement('section');
        panel.className = 'markdown-preview-panel';
        panel.innerHTML = [
            '<div class="markdown-preview-header">',
            '<strong>文章预览</strong>',
            '<span>目录会读取 ## / ### 标题</span>',
            '</div>',
            '<div class="markdown-preview-content"></div>'
        ].join('');

        textarea.insertAdjacentElement('afterend', panel);
        var content = panel.querySelector('.markdown-preview-content');
        var update = function () {
            content.innerHTML = renderMarkdown(textarea.value);
        };

        textarea.addEventListener('input', update);
        update();
    }

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('textarea[data-markdown-editor="true"]').forEach(attachPreview);
    });
})();
