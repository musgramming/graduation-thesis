const directBoard = function(){
    window.addEventListener('contextmenu', function (e) { 
        e.preventDefault(); 
    }, false);

    // 1. Khi chuột rời khỏi cửa sổ trình duyệt
    window.addEventListener('mouseleave', function() {
        const mainContent = document.querySelector('main') || document.body;
        if (mainContent) {
            mainContent.style.filter = 'blur(50px)';
            mainContent.style.transition = '0.1s';
        }
    });

    // 2. Khi chuột quay lại
    window.addEventListener('mouseenter', function() {
        const mainContent = document.querySelector('main') || document.body;
        if (mainContent) {
            mainContent.style.filter = 'none';
        }
    });

    // Cấm các phím tắt (đã chuẩn hóa dấu phẩy ở mọi phần tử trong mảng)
    window.addEventListener('keydown', function (e) {
        const isCtrl = e.ctrlKey;
        const isShift = e.shiftKey;
        const isWindow = e.metaKey;

        let key = e.key.toLowerCase();
        const forbidden = [
            (isCtrl && key === "u"),
            (key === "f12"),
            (isCtrl && key === "s"),
            (isCtrl && isShift && key === "s"),
            (isWindow && isShift && key === "s"),  // Đã có dấu phẩy chuẩn
            (isCtrl && key === "c"),               // Đã có dấu phẩy chuẩn
            (isCtrl && key === "a"),               // Đã có dấu phẩy chuẩn
            (isCtrl && key === "p"),               // Đã có dấu phẩy chuẩn
            (isCtrl && isShift && key === "i"),    // Đã có dấu phẩy chuẩn
            (isCtrl && isShift && key === "c"),    // Đã có dấu phẩy chuẩn
            (isCtrl && isShift && key === "j")     // Phần tử cuối không cần phẩy cũng được
        ];

        if (forbidden.some(condition => condition)) {
            e.preventDefault();
            return false;
        }
    });
};

const isLocal = window.location.hostname === 'localhost' || 
                window.location.hostname === '127.0.0.1' || 
                window.location.hostname.startsWith('192.168.');

if (!isLocal){
    directBoard();
}