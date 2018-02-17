var USERNAME = "";
var pleer = false;

BaasBox.setEndPoint('http://localhost:9000');
BaasBox.appcode = '1234567890';

BaasBox.fetchCurrentUser()
    .done(function(res) { logged(res.data.user.name); })
    .fail(function(error) {
        window.location.replace('/login');
        console.log("error1 ", error);
        $('#up_login').show()
    })

function battleClick(id) {
    BaasBox.fetchFile(id).done(function(res) {
        pleer.play(JSON.parse(res));
    }).fail(function(error) {
        console.log("error ", error);
    });
}

var prev_select = 'nothing';
var prev_top = 'nothing';
function battlesSelect() {
    var $sel = $('#battles-select');
    var params = {'recordsPerPage': 100, 'page':0, 'orderBy': '_creation_date desc'}

    if ($sel.val() == 'with-me') {
        params['where'] = "body.user1='" + USERNAME + "' or body.user2='" + USERNAME + "'";
    }

    BaasBox.loadCollectionWithParams("battles", params) .done(function(res) {
        if (prev_select == $sel.val() && prev_top == res[0].id) {
            return;
        }

        console.log('redraw battle list');
        prev_select = $sel.val();
        prev_top = res[0].id;

        var html = $.templates('#battle-template').render(res.map(function(x){
            d = new Date(x._creation_date);
            r = x.body;
            r.date = d.toLocaleString('ru', {month: '2-digit', day: '2-digit', hour: '2-digit', minute:'2-digit'})
            return r;
        }));
        $('#battles-list').html(html);
    }).fail(function(error) {
        console.log("error ", error);
    });
}

function logged(username) {
    USERNAME = username;
    console.log("logged ", username);
    $('#user_name').html('Hi ' + username);
    $('#up_login').hide();
    $('#up_logged').show();

    $.post('get_versions', function(data) {
        console.log('x', data);
        var html = Object.keys(data).map(function(name) { return '<option>' + name + '</option>' }).join()
        $('#user1').html('<option disabled selected>user 1</option>' + html).change(function() {
            var ver = data[$(this).val()];
            var html = [...Array(ver).keys()].map(function(v) { return '<option>' + (ver - v) + '</option>'; }).join();
            $('#version1').html(html).val(ver.toString());
        });
        $('#user2').html('<option disabled selected>user 2</option>' + html).change(function() {
            var ver = data[$(this).val()];
            var html = [...Array(ver).keys()].map(function(v) { return '<option>' + (ver - v) + '</option>'; }).join();
            $('#version2').html(html).val(ver.toString());
        });
    });
    BaasBox.fetchFilesDetails().done(function(res) {
        console.log(res);
    }).fail(function(err) {
        console.log('error ', err);
    });

    $('#battles-select').change();

    $.post('get_results', function(data) {
        console.log('x', data);
        var html = $.templates('#result-template').render(data);
        $('#results').html(html);
        for (i in data) {
            if (data[i].name == username) {
                $('#user_name').html(username + ' [№' + i + ' ~' + data[i].mean.toFixed(2) + ']');
            }
        }
    });

    setInterval(battlesSelect, 5000);
}

$(document).ready(function() {
    pleer = new Pleer(800, 600);

    $('#login_btn').click(function() {
        BaasBox.login($('#login').val(), $('#password').val())
            .done(function (data) {
                logged(data.username);
            })
        .fail(function (err) {
            console.log('error ', err);
        })
    });
    $('#signup_btn').click(function() {
        BaasBox.signup($('#login').val(), $('#password').val())
            .done(function (res) { logged(res.data.user.name); })
            .fail(function (error) {
                console.log('error ', error);
            })
    });
    $('#logout_btn').click(function() {
        BaasBox.logout()
            .done(function(res) {
                console.log("res ", res['data']);
                $('#up_logged').hide();
                $('#up_login').show();
            })
        .fail(function(error) {
            console.log("error ", error);
        })
    });
    $("#upload_form").submit(function(e) {
        e.preventDefault();
        var formObj = $(this);
        var formData = new FormData(this);
        BaasBox.uploadFile(formData).done(function(res) {
            console.log("res ", JSON.parse(res));
            console.log(JSON.parse(res).data.id)
        }).fail(function(error) {
            console.log("error ", error);
        })
    });
    $("#battle_form").submit(function(e) {
        e.preventDefault();
        var formObj = $(this);
        var formData = new FormData(this);
        console.log($(this).serialize());
        $.post('battle', $(this).serialize(), function(data) {
            console.log(data);
        });
    });
    $("#pleer-toggle").click(function() { pleer.toggle() });
    $('#pleer-pos').change(function() { pleer.jump(parseInt($(this).val())); });
    $('#pleer-pos').mousedown(function() { pleer.freeze(); });
    $('#pleer-pos').mouseup(function() { pleer.unfreeze(); });
    $('#battles-select').change(battlesSelect);
});
