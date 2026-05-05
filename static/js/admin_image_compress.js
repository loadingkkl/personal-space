(function () {
    var MAX_WIDTH = 1600;
    var MAX_HEIGHT = 1200;
    var TARGET_BYTES = 1500 * 1024;
    var MIN_QUALITY = 0.68;

    function formatSize(bytes) {
        if (!bytes) return '0 KB';
        if (bytes >= 1024 * 1024) return (bytes / 1024 / 1024).toFixed(1) + ' MB';
        return Math.round(bytes / 1024) + ' KB';
    }

    function makeStatus(input) {
        var status = document.createElement('p');
        status.className = 'admin-image-compress-status';
        status.style.margin = '6px 0 0';
        status.style.color = '#475569';
        status.style.fontSize = '12px';
        input.insertAdjacentElement('afterend', status);
        return status;
    }

    function readAsImage(file) {
        return new Promise(function (resolve, reject) {
            var url = URL.createObjectURL(file);
            var image = new Image();
            image.onload = function () {
                URL.revokeObjectURL(url);
                resolve(image);
            };
            image.onerror = function () {
                URL.revokeObjectURL(url);
                reject(new Error('Failed to read image'));
            };
            image.src = url;
        });
    }

    function canvasToBlob(canvas, type, quality) {
        return new Promise(function (resolve) {
            canvas.toBlob(resolve, type, quality);
        });
    }

    function scaledSize(width, height) {
        var ratio = Math.min(1, MAX_WIDTH / width, MAX_HEIGHT / height);
        return {
            width: Math.max(1, Math.round(width * ratio)),
            height: Math.max(1, Math.round(height * ratio))
        };
    }

    async function compressImage(file) {
        var image = await readAsImage(file);
        var size = scaledSize(image.naturalWidth || image.width, image.naturalHeight || image.height);
        var canvas = document.createElement('canvas');
        canvas.width = size.width;
        canvas.height = size.height;
        var context = canvas.getContext('2d');
        context.drawImage(image, 0, 0, size.width, size.height);

        var type = 'image/jpeg';
        var quality = 0.86;
        var blob = await canvasToBlob(canvas, type, quality);
        while (blob && blob.size > TARGET_BYTES && quality > MIN_QUALITY) {
            quality = Math.max(MIN_QUALITY, quality - 0.08);
            blob = await canvasToBlob(canvas, type, quality);
        }

        if (!blob || blob.size >= file.size) {
            return file;
        }

        var baseName = file.name.replace(/\.[^.]+$/, '') || 'cover';
        return new File([blob], baseName + '.jpg', {
            type: type,
            lastModified: Date.now()
        });
    }

    function replaceFile(input, file) {
        var transfer = new DataTransfer();
        transfer.items.add(file);
        input.files = transfer.files;
    }

    function shouldHandle(input) {
        return input.type === 'file' && input.name === 'cover' && input.files && input.files[0];
    }

    function attachBodyGuard() {
        var body = document.querySelector('textarea[name="body"]');
        if (!body) return;

        var form = body.closest('form');
        if (!form) return;

        form.addEventListener('submit', function (event) {
            if (body.value.indexOf('data:image/') !== -1) {
                event.preventDefault();
                window.alert('正文里不能直接粘贴 base64 图片，请先上传到 Cloudinary 后使用图片 URL。');
            }
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        attachBodyGuard();

        document.querySelectorAll('input[type="file"][name="cover"]').forEach(function (input) {
            input.accept = 'image/*';
            var status = makeStatus(input);
            var form = input.closest('form');

            if (form) {
                form.addEventListener('submit', function (event) {
                    if (input.dataset.compressing === 'true') {
                        event.preventDefault();
                        status.textContent = '图片还在压缩，请稍后再提交。';
                    }
                });
            }

            input.addEventListener('change', async function () {
                if (!shouldHandle(input)) return;
                var original = input.files[0];
                if (!original.type || original.type.indexOf('image/') !== 0) return;

                status.textContent = '正在压缩图片...';
                input.dataset.compressing = 'true';
                try {
                    var compressed = await compressImage(original);
                    if (compressed !== original) {
                        replaceFile(input, compressed);
                        status.textContent = '已压缩：' + formatSize(original.size) + ' -> ' + formatSize(compressed.size);
                    } else {
                        status.textContent = '图片大小合适：' + formatSize(original.size);
                    }
                } catch (error) {
                    status.textContent = '自动压缩失败，请改用 3MB 以内的图片。';
                } finally {
                    input.dataset.compressing = 'false';
                }
            });
        });
    });
})();
