
window.onload = function() {

    const displacy = new displaCy('/', {
        container: '#displacy',
        format: "spacy",
        distance: 300,
        offsetX: 100,
        bg: "#455a64",
        color: "#fff",
        wordSpacing: 40,
    });

    function process(text) {
        $("#displacy").hide();
        $("#progress").show();

        $.ajax({
            contentType: 'application/json',
            data: text,
            dataType: 'json',
            success: data => {
                $("#progress").hide();
                $("#displacy").show();
                displacy.render(data);
            },
            error: () => {
                console.error('Failed to receive data for text' + text);
                $("progress").hide();
            },
            processData: false,
            type: 'POST',
            url: '/process'
        });
    }


    // listen for enter pressed
    const input = $('input');
    input.keypress( (e) => {
        if( e.which === 13 ) {
            process($('#input').val());
        }
    });

    // trigger enter press onStart
    const e = $.Event( "keypress", { which: 13 } );
    input.trigger(e);
};