
window.onload = function() {

    const displacy = new displaCy('/', {
        container: '#displacy',
        format: "spacy",
        distance: 250,
        offsetX: 100,
        bg: "#455a64",
        color: "#fff",
        wordSpacing: 40,
    });

    function process(text) {
        $("#displacy").hide();
        $("#error").hide();
        $("#progress").show();

        $.ajax({
            contentType: 'application/json',
            data: text,
            dataType: 'json',
            success: data => {
                $("#progress").hide();
                $("#error").hide();
                $("#displacy").show();
                displacy.render(data);
            },
            error: () => {
                $("#displacy").hide();
                $("#progress").hide();
                $("#error").show();
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


    ////////////////////////// Error ////////////////////////
    const root = document.documentElement;
    const eyef = document.getElementById('eyef');
    let cx = document.getElementById("eyef").getAttribute("cx");
    let cy = document.getElementById("eyef").getAttribute("cy");

    document.addEventListener("mousemove", evt => {
      let x = evt.clientX / innerWidth;
      let y = evt.clientY / innerHeight;

      root.style.setProperty("--mouse-x", x);
      root.style.setProperty("--mouse-y", y);

      cx = 115 + 30 * x;
      cy = 50 + 30 * y;
      eyef.setAttribute("cx", cx);
      eyef.setAttribute("cy", cy);

    });

    document.addEventListener("touchmove", touchHandler => {
      let x = touchHandler.touches[0].clientX / innerWidth;
      let y = touchHandler.touches[0].clientY / innerHeight;

      root.style.setProperty("--mouse-x", x);
      root.style.setProperty("--mouse-y", y);
    });
};