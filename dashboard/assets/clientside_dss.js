window.dash_clientside = Object.assign({}, window.dash_clientside, {
    withSBD: {
        /**
         * Cấu hình Slider chọn điểm sàn dựa trên điểm của thí sinh.
         *
         * Quy tắc:
         *
         * - Điểm tối thiểu của Slider là 15.
         * - Điểm tối đa là min(30, điểm của thí sinh).
         * - Nếu điểm của thí sinh < 15, Slider bị vô hiệu hóa
         *   và hiển thị cảnh báo.
         * - Nếu điểm hợp lệ, Slider được kích hoạt và marks được
         *   tạo tự động.
         *
         * Hàm chỉ xử lý presentation/UI state và được thực thi
         * hoàn toàn ở phía client.
         *
         * @param {string|null} scoreText
         *     Điểm của thí sinh ở dạng chuỗi hiển thị,
         *     ví dụ "25.50 điểm".
         *
         * @returns {Array}
         *     Mảng kết quả tương ứng với các Output của
         *     Dash clientside callback:
         *
         *     [
         *         max,
         *         marks,
         *         value,
         *         disabled,
         *         warningChildren,
         *         warningIsOpen
         *     ]
         */
        configure_floor_score: function (scoreText) {
            const MIN_SCORE = 15;

            if (typeof scoreText !== "string") {
                return [
                    30,
                    {15: "15"},
                    15,
                    true,
                    "",
                    false
                ];
            }

            const match = scoreText.match(/^\s*(\d+(?:\.\d+)?)/);

            if (!match) {
                return [
                    30,
                    {15: "15"},
                    15,
                    true,
                    "",
                    false
                ];
            }

            const score = Number(match[1]);

            if (!Number.isFinite(score)) {
                return [
                    30,
                    {15: "15"},
                    15,
                    true,
                    "",
                    false
                ];
            }

            // Điểm thực tế < 15
            if (score < MIN_SCORE) {
                return [
                    30,
                    {15: "15"},
                    15,
                    true,
                    "Điểm sàn tối thiểu từ 15.00 trở lên",
                    true
                ];
            }

            // Tổng điểm 3 môn nên score <= 30
            const maxScore = score;

            const marks = {};

            for (
                let value = MIN_SCORE;
                value <= Math.floor(maxScore);
                value += 3
            ) {
                marks[value] = String(value);
            }

            // Luôn đánh dấu điểm tối đa
            if (!marks[maxScore]) {
                marks[maxScore] = maxScore.toFixed(2);
            }

            return [
                maxScore,
                marks,
                MIN_SCORE,
                false,
                "",
                false
            ];
        },




        
        /**
         * Xác định trạng thái disabled của nút Xây kịch bản.
         *
         * Nút chỉ được kích hoạt khi:
         *
         * - Điểm thí sinh có định dạng hợp lệ.
         * - Có ít nhất một tổ hợp được chọn.
         * - Slider điểm sàn đã được kích hoạt.
         *
         * Hàm chỉ kiểm tra trạng thái giao diện nên được thực thi
         * hoàn toàn ở phía client.
         *
         * @param {string|null} scoreText
         *     Điểm thí sinh ở dạng chuỗi, ví dụ "25.50 điểm".
         *
         * @param {Array<string>|null} combs
         *     Danh sách các tổ hợp được chọn.
         *
         * @param {boolean} sliderDisabled
         *     Trạng thái disabled hiện tại của Slider điểm sàn.
         *
         * @returns {boolean}
         *     true nếu nút phải disabled;
         *     false nếu nút có thể được kích hoạt.
         */
        toggle_analysis_button: function (
            scoreText,
            combs,
            sliderDisabled
        ) {
            const validScore =
                typeof scoreText === "string" &&
                /^\s*\d+(?:\.\d+)?\s+điểm\s*$/.test(scoreText);

            const validCombs =
                Array.isArray(combs) &&
                combs.length > 0;

            return !(
                validScore &&
                validCombs &&
                sliderDisabled === false
            );
        }, 





        /**
         * Chuyển đổi và chuẩn hóa giá trị từ ô nhập liệu (Input) sang Slider.
         *
         * Thực hiện kiểm tra tính hợp lệ, làm tròn theo bước nhảy (step = 0.05)
         * và giới hạn giá trị trong khoảng cho phép của Slider [min, max].
         *
         * @param {number|string|null} value
         *     Giá trị hiện tại từ ô nhập liệu.
         *
         * @param {number} min
         *     Giá trị tối thiểu cho phép của Slider.
         *
         * @param {number} max
         *     Giá trị tối đa cho phép của Slider.
         *
         * @returns {number|string}
         *     Giá trị đã được chuẩn hóa hoặc dash_clientside.no_update nếu không hợp lệ.
         */
        input_to_slider: function (value, min, max) {
            if (value === null || value === undefined) {
                return window.dash_clientside.no_update;
            }

            value = Number(value);

            if (!Number.isFinite(value)) {
                return window.dash_clientside.no_update;
            }

            // Làm tròn theo step = 0.05
            value = Math.round(value / 0.05) * 0.05;

            // Giới hạn trong khoảng của Slider
            value = Math.max(min, Math.min(max, value));

            return Number(value.toFixed(2));
        },





        /**
         * Chuyển đổi và định dạng giá trị từ Slider sang ô nhập liệu (Input).
         *
         * Đảm bảo giá trị trả về có định dạng số hợp lệ với tối đa 2 chữ số thập phân.
         *
         * @param {number|null} value
         *     Giá trị hiện tại từ Slider.
         *
         * @returns {number|string}
         *     Giá trị số đã làm tròn 2 chữ số thập phân hoặc dash_clientside.no_update nếu không hợp lệ.
         */
        slider_to_input: function (value) {
            if (value === null || value === undefined) {
                return window.dash_clientside.no_update;
            }

            return Number(Number(value).toFixed(2));
        },
    }, 





    withoutSbd: {

        /**
         * Đồng bộ hai Dropdown môn tự chọn.
         *
         * Đảm bảo môn 1 và môn 2 luôn khác nhau.
         * Khi một môn được chọn, môn đó sẽ bị loại khỏi
         * danh sách options của Dropdown còn lại.
         *
         * @param {string|null} mon1
         *     Môn tự chọn thứ nhất.
         *
         * @param {string|null} mon2
         *     Môn tự chọn thứ hai.
         *
         * @returns {Array}
         *     [
         *         options của mon-1,
         *         value của mon-1,
         *         options của mon-2,
         *         value của mon-2
         *     ]
         */
        sync_subjects: function (mon1, mon2) {
            const allOptions = [
                {"label": "Lí", "value": "Lí"},
                {"label": "Hóa", "value": "Hóa"},
                {"label": "Sinh", "value": "Sinh"},
                {"label": "Sử", "value": "Sử"},
                {"label": "Địa", "value": "Địa"},
                {"label": "GDKT&PL", "value": "GDKT&PL"},
                {"label": "Tin", "value": "Tin"},
                {"label": "Công nghệ", "value": "Công nghệ"}
            ];

            /*
                * Trạng thái khởi tạo.
                *
                * Layout mặc định:
                *     mon-1 = Lí
                *     mon-2 = Hóa
                */
            if (!mon1 && !mon2) {
                return [
                    allOptions.filter(
                        option => option.value !== "Hóa"
                    ),
                    "Lí",

                    allOptions.filter(
                        option => option.value !== "Lí"
                    ),
                    "Hóa"
                ];
            }

            /*
            * Nếu một Dropdown chưa có value,
            * chọn một môn hợp lệ khác với Dropdown còn lại.
            */
            if (!mon1) {
                const replacement = allOptions.find(
                    option => option.value !== mon2
                );

                mon1 = replacement
                    ? replacement.value
                    : null;
            }

            if (!mon2) {
                const replacement = allOptions.find(
                    option => option.value !== mon1
                );

                mon2 = replacement
                    ? replacement.value
                    : null;
            }

            /*
            * Nếu hai Dropdown vô tình có cùng value,
            * giữ mon1 và thay mon2 bằng môn khác.
            */
            if (mon1 === mon2 && mon1 !== null) {
                const replacement = allOptions.find(
                    option => option.value !== mon1
                );

                if (replacement) {
                    mon2 = replacement.value;
                }
            }

            const options1 = allOptions.filter(
                option => option.value !== mon2
            );

            const options2 = allOptions.filter(
                option => option.value !== mon1
            );

            return [
                options1,
                mon1,
                options2,
                mon2
            ];
        },





        /**
         * Kiểm tra bốn điểm trước khi cho phép
         * tính toán điểm tổ hợp.
         *
         * Điều kiện hợp lệ:
         *
         * - Tất cả điểm đều đã có giá trị.
         * - Tất cả điểm nằm trong khoảng [0, 10].
         * - Không có điểm nào <= 1.
         *
         * @param {number|null} toan
         *     Điểm Toán.
         *
         * @param {number|null} van
         *     Điểm Văn.
         *
         * @param {number|null} mon1
         *     Điểm môn tự chọn thứ nhất.
         *
         * @param {number|null} mon2
         *     Điểm môn tự chọn thứ hai.
         *
         * @returns {boolean}
         *     true  -> nút bị disabled.
         *     false -> nút được phép sử dụng.
         */
        validate_scores: function (toan, van, mon1, mon2) 
        {
            const scores = [toan, van, mon1, mon2].map(Number);

            return scores.some(
                value =>
                    !Number.isFinite(value) ||
                    value < 0 ||
                    value > 10 ||
                    value <= 1
            );
        },





        /**
         * Cấu hình và đồng bộ điểm sàn.
         *
         * Callback này thay thế hai callback Python:
         *
         *     update_slider_limits()
         *     sync_slider_and_input()
         *
         * Điểm tối đa được giới hạn bởi:
         *
         *     min(30, điểm tổ hợp của thí sinh)
         *
         * Đồng thời đồng bộ:
         *
         *     Slider <-> Numeric Input
         *
         * @param {string|number|null} scoreText
         *     Điểm tổ hợp, ví dụ:
         *     "25.50 điểm"
         *
         * @param {number|null} sliderValue
         *     Giá trị hiện tại của Slider.
         *
         * @param {number|null} inputValue
         *     Giá trị hiện tại của Numeric Input.
         *
         * @returns {Array}
         *     [
         *         slider max,
         *         slider value,
         *         input max,
         *         input value
         *     ]
         */
        sync_floor_score: function (scoreText, sliderValue, inputValue) 
        {
            const MIN_SCORE = 15;
            const DEFAULT_MAX = 30;

            let score = Number.NaN;

            /*
                * Trường hợp scoreText đã là number.
                */
            if (typeof scoreText === "number")
            {
                score = scoreText;
            }
                /*
                * Trường hợp scoreText là chuỗi:
                *
                *     "25.50 điểm"
                *
                * Lấy phần số ở đầu chuỗi.
                */
            else if (typeof scoreText === "string") 
            {
                const match = scoreText.match(
                    /^\s*(\d+(?:\.\d+)?)/
                );

                if (match) {
                    score = Number(match[1]);
                }
            }

            /*
                * Tính giới hạn trên.
                */
            const maxScore = Number.isFinite(score)
                ? Math.min(DEFAULT_MAX, score)
                : DEFAULT_MAX;

            let nextSlider =
                Number.isFinite(sliderValue)
                    ? sliderValue
                    : MIN_SCORE;

            let nextInput =
                Number.isFinite(inputValue)
                    ? inputValue
                    : MIN_SCORE;

            /*
                * Nếu điểm hiện tại vượt quá max mới
                * thì đưa cả hai về điểm sàn tối thiểu.
                */
            if (
                nextSlider > maxScore ||
                nextInput > maxScore ||
                maxScore < MIN_SCORE
            ) {
                nextSlider =
                    Math.min(
                        MIN_SCORE,
                        maxScore
                    );

                nextInput =
                    Math.min(
                        MIN_SCORE,
                        maxScore
                    );
            }

            /*
                * Không cho điểm sàn thấp hơn 15.
                */
            nextSlider = Math.max(
                MIN_SCORE,
                nextSlider
            );

            nextInput = Math.max(
                MIN_SCORE,
                nextInput
            );

            /*
                * Không cho điểm sàn vượt quá điểm tối đa.
                */
            nextSlider = Math.min(
                maxScore,
                nextSlider
            );

            nextInput = Math.min(
                maxScore,
                nextInput
            );

            return [
                maxScore,
                nextSlider,
                maxScore,
                nextInput
            ];
        }
    }
});