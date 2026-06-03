window.addEventListener('contextmenu', function (e) { 
  e.preventDefault(); 
}, false);



// 1. Khi chuột rời khỏi cửa sổ trình duyệt, làm mờ ngay lập tức
window.addEventListener('mouseleave', function() {
    const mainContent = document.querySelector('main') || document.body;
    if (mainContent) {
        mainContent.style.filter = 'blur(50px)';
        mainContent.style.transition = '0.1s'; // Làm mờ cực nhanh (0.1 giây)
    }
});



// 2. Khi chuột quay lại, hiện lại bình thường
window.addEventListener('mouseenter', function() {
    const mainContent = document.querySelector('main') || document.body;
    if (mainContent) {
        mainContent.style.filter = 'none';
    }
});



// Cấm các nút (Trừ mấy cái cho nhập như Input, Dropdown,...)
window.addEventListener('keydown', function (e) {
    // Các phím tắt nguy hiểm thường đi kèm với Ctrl (hoặc Command trên Mac)
    const isCtrl = e.ctrlKey;
    const isShift = e.shiftKey;
    const isWindow = e.metaKey;

    // Danh sách các "phím cấm"
    let key = e.key.toLowerCase()
    const forbidden = [
        // Ctrl + U --> Source
        // F12 --> Source
        (isCtrl && key === "u"),
        (key === "f12"),

        // Ctrl + S --> Save
        // Ctrl + Shift + S --> Save as a page
        // Window + Shift + S --> Picturing
        (isCtrl && key === "s"),
        (isCtrl && isShift && key === "s"),
        (isWindow && isShift && key === "s")

        // Ctrl + C --> Copy
        (isCtrl && key === "c"),

        // Ctrl + A --> Choose all
        (isCtrl && key === "a"),

        // Ctrl + P --> Print
        (isCtrl && key === "p"),

        // DevTools 
        // - (Ctrl + Shift + I)
        // - (Ctrl + Shift + C)
        // - (Ctrl + Shift + J) --> Console
        (isCtrl && isShift && key === "i"),
        (isCtrl && isShift && key === "c"),
        (isCtrl && isShift && key === "j"),
    ];


    if (forbidden.some(condition => condition)) {
        e.preventDefault();
        return false;
    }
});

setInterval(function() {
    console.clear();
}, 1000);
