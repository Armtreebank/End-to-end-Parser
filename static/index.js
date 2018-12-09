
window.onload = function() {

    const displacy = new displaCy('/', {
        container: '#displacy',
        format: 'spacy',
        distance: 300,
        offsetX: 100,
        bg: "#455a64",
        color: "#fff",
        wordSpacing: 40,
    });

    function process(text) {
        displacy.render({words: [], arcs: []});

        $.ajax({
            contentType: 'application/json',
            data: text,
            dataType: 'json',
            success: data => {
                displacy.render(data)
            },
            error: () => console.error('Failed to receive data for text' + text),
            processData: false,
            type: 'POST',
            url: '/process'
        });
    }

    $('input').keypress( (e) => {
        if( e.key === 'Enter' ) {
            process($('#input').val());
        }
    });
};