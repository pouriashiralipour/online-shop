function convertToPersianNumbers(element = document) {
    const persianDigits = {
        '0': '۰',
        '1': '۱',
        '2': '۲',
        '3': '۳',
        '4': '۴',
        '5': '۵',
        '6': '۶',
        '7': '۷',
        '8': '۸',
        '9': '۹'
    };

    const walker = document.createTreeWalker(
        element,
        NodeFilter.SHOW_TEXT,
        {
            acceptNode: function(node) {
                if (['INPUT', 'TEXTAREA', 'SCRIPT'].includes(node.parentElement.tagName)) {
                    return NodeFilter.FILTER_REJECT;
                }
                return NodeFilter.FILTER_ACCEPT;
            }
        }
    );

    const nodes = [];
    let node;
    while (node = walker.nextNode()) {
        nodes.push(node);
    }

    nodes.forEach(node => {
        let text = node.textContent;
        for (const [engDigit, persianDigit] of Object.entries(persianDigits)) {
            text = text.replace(new RegExp(engDigit, 'g'), persianDigit);
        }
        node.textContent = text;
    });
}

document.addEventListener('DOMContentLoaded', () => {
    convertToPersianNumbers();
});
