const directBoard = function(){
    // 1. Chặn chuột phải
    window.addEventListener('contextmenu', function (e) { 
        e.preventDefault(); 
    }, false);

    // 2. Khi chuột rời khỏi cửa sổ trình duyệt
    window.addEventListener('mouseleave', function() {
        const mainContent = document.querySelector('main') || document.body;
        if (mainContent) {
            mainContent.style.filter = 'blur(50px)';
            mainContent.style.transition = '0.1s';
        }
    });

    // 3. Khi chuột quay lại
    window.addEventListener('mouseenter', function() {
        const mainContent = document.querySelector('main') || document.body;
        if (mainContent) {
            mainContent.style.filter = 'none';
        }
    });

    // 4. [MỚI] Khi đổi tab, ấn Alt+Tab hoặc thu nhỏ trình duyệt (Visibility Change)
    document.addEventListener('visibilitychange', function() {
        const mainContent = document.querySelector('main') || document.body;
        if (mainContent) {
            if (document.hidden) {
                mainContent.style.filter = 'blur(50px)';
                mainContent.style.transition = '0.1s';
            } else {
                mainContent.style.filter = 'none';
            }
        }
    });

    // 5. Cấm các phím tắt (đã chuẩn hóa dấu phẩy ở mọi phần tử trong mảng)
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
            (isWindow && isShift && key === "s"),  
            (isCtrl && key === "c"),               
            (isCtrl && key === "a"),               
            (isCtrl && key === "p"),               
            (isCtrl && isShift && key === "i"),    
            (isCtrl && isShift && key === "c"),    
            (isCtrl && isShift && key === "j")     
        ];

        if (forbidden.some(condition => condition)) {
            e.preventDefault();
            return false;
        }
    });
};



if (window.APP_ENV === 'production') {
    directBoard();
    console.log("🔒 Chế độ Production: Kích hoạt bảo vệ Client-side.");
} else {
    console.log("🛠️ Chế độ Development: Tắt bảo vệ để tiện lập trình.");
}