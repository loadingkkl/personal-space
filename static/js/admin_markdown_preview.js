(function () {
    function escapeHtml(value) {
        return value
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function inlineMarkdown(value) {
        return escapeHtml(value)
            .replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1">')
            .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
            .replace(/\*([^*]+)\*/g, '<em>$1</em>');
    }

    function renderMarkdown(value) {
        var html = [];
        var paragraph = [];
        var list = [];
        var ordered = [];
        var inCode = false;
        var codeLang = '';
        var codeLines = [];

        function flushParagraph() {
            if (!paragraph.length) return;
            html.push('<p>' + paragraph.map(inlineMarkdown).join('<br>') + '</p>');
            paragraph = [];
        }

        function flushList() {
            if (list.length) {
                html.push('<ul>' + list.map(function (item) {
                    return '<li>' + inlineMarkdown(item) + '</li>';
                }).join('') + '</ul>');
                list = [];
            }
            if (ordered.length) {
                html.push('<ol>' + ordered.map(function (item) {
                    return '<li>' + inlineMarkdown(item) + '</li>';
                }).join('') + '</ol>');
                ordered = [];
            }
        }

        value.split(/\r?\n/).forEach(function (rawLine) {
            var line = rawLine.trim();
            var orderedMatch = line.match(/^\d+\.\s+(.+)$/);

            if (line.indexOf('```') === 0) {
                flushParagraph();
                flushList();
                if (inCode) {
                    html.push(
                        '<pre><code class="language-' + escapeHtml(codeLang) + '">' +
                        escapeHtml(codeLines.join('\n')) +
                        '</code></pre>'
                    );
                    inCode = false;
                    codeLang = '';
                    codeLines = [];
                } else {
                    inCode = true;
                    codeLang = line.slice(3).trim();
                }
                return;
            }

            if (inCode) {
                codeLines.push(rawLine);
                return;
            }

            if (!line) {
                flushParagraph();
                flushList();
                return;
            }

            if (line.indexOf('### ') === 0 && line.slice(4).trim()) {
                flushParagraph();
                flushList();
                html.push('<h3>' + inlineMarkdown(line.slice(4).trim()) + '</h3>');
                return;
            }

            if (line.indexOf('## ') === 0 && line.slice(3).trim()) {
                flushParagraph();
                flushList();
                html.push('<h2>' + inlineMarkdown(line.slice(3).trim()) + '</h2>');
                return;
            }

            if (line.indexOf('# ') === 0 && line.slice(2).trim()) {
                flushParagraph();
                flushList();
                html.push('<h1>' + inlineMarkdown(line.slice(2).trim()) + '</h1>');
                return;
            }

            if (line.indexOf('> ') === 0 && line.slice(2).trim()) {
                flushParagraph();
                flushList();
                html.push('<blockquote>' + inlineMarkdown(line.slice(2).trim()) + '</blockquote>');
                return;
            }

            if (line.indexOf('- ') === 0 && line.slice(2).trim()) {
                flushParagraph();
                ordered = [];
                list.push(line.slice(2).trim());
                return;
            }

            if (orderedMatch) {
                flushParagraph();
                list = [];
                ordered.push(orderedMatch[1]);
                return;
            }

            flushList();
            paragraph.push(rawLine);
        });

        flushParagraph();
        flushList();

        if (inCode) {
            html.push('<pre><code>' + escapeHtml(codeLines.join('\n')) + '</code></pre>');
        }

        return html.join('') || '<p class="markdown-preview-empty">开始输入正文后，这里会显示预览。</p>';
    }

    function wrapSelection(textarea, before, after, fallback) {
        var start = textarea.selectionStart;
        var end = textarea.selectionEnd;
        var selected = textarea.value.slice(start, end) || fallback;
        var replacement = before + selected + after;
        textarea.setRangeText(replacement, start, end, 'select');
        textarea.dispatchEvent(new Event('input', { bubbles: true }));
        textarea.focus();
    }

    function insertAtCursor(textarea, text) {
        textarea.setRangeText(text, textarea.selectionStart, textarea.selectionEnd, 'end');
        textarea.dispatchEvent(new Event('input', { bubbles: true }));
        textarea.focus();
    }

    function makeButton(label, title, handler) {
        var button = document.createElement('button');
        button.type = 'button';
        button.className = 'markdown-toolbar-btn';
        button.textContent = label;
        button.title = title;
        button.addEventListener('click', handler);
        return button;
    }

    function attachPreview(textarea) {
        var shell = document.createElement('section');
        shell.className = 'markdown-editor-shell';

        var toolbar = document.createElement('div');
        toolbar.className = 'markdown-toolbar';
        toolbar.append(
            makeButton('H2', '插入二级标题', function () { insertAtCursor(textarea, '\n## 小标题\n'); }),
            makeButton('H3', '插入三级标题', function () { insertAtCursor(textarea, '\n### 小节标题\n'); }),
            makeButton('B', '加粗', function () { wrapSelection(textarea, '**', '**', '加粗文字'); }),
            makeButton('I', '斜体', function () { wrapSelection(textarea, '*', '*', '斜体文字'); }),
            makeButton('Link', '插入链接', function () { wrapSelection(textarea, '[', '](https://example.com)', '链接文字'); }),
            makeButton('Img', '插入图片', function () {
                var url = window.prompt('图片 URL，例如 Cloudinary 地址或 /media/... 路径');
                if (url) insertAtCursor(textarea, '\n![图片说明](' + url.trim() + ')\n');
            }),
            makeButton('Code', '插入代码块', function () { insertAtCursor(textarea, '\n```python\nprint(\"hello\")\n```\n'); }),
            makeButton('Quote', '插入引用', function () { insertAtCursor(textarea, '\n> 引用内容\n'); })
        );

        var panel = document.createElement('section');
        panel.className = 'markdown-preview-panel';
        panel.innerHTML = [
            '<div class="markdown-preview-header">',
            '<strong>文章预览</strong>',
            '<span>保存后前台会使用 Markdown 渲染并自动生成目录</span>',
            '</div>',
            '<div class="markdown-preview-content"></div>'
        ].join('');

        textarea.parentNode.insertBefore(shell, textarea);
        shell.appendChild(toolbar);
        shell.appendChild(textarea);
        shell.appendChild(panel);

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
