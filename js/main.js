var USERNAME = "";
var pleer = false;

var cur_show_all = false;

BaasBox.setEndPoint('http://ai-contest.vdi.mipt.ru/baasbox');
//BaasBox.setEndPoint('http://localhost:9000');
BaasBox.appcode = '1234567890';


function battleClick(id) {
    BaasBox.fetchFile(id).done(function(res) {
        pleer.play(JSON.parse(res));
    }).fail(function(error) {
        console.log("error ", error);
    });
}

var prev_select = 'nothing';
var prev_top = 'nothing';
function battlesSelect(user1, user2) {
    var $sel = $('#battles-select');
    var params = {'recordsPerPage': 100, 'page':0, 'orderBy': '_creation_date desc'}

    params['where'] = "body.user1='" + user1 + "' and body.user2='" + user2 + "' or ";
    params['where'] += "body.user1='" + user2 + "' and body.user2='" + user1 + "'";

    BaasBox.loadCollectionWithParams("battles", params) .done(function(res) {
        if (prev_select == $sel.val() && res.length > 0 &&  prev_top == res[0].id) {
            return;
        }

        console.log('redraw battle list');
        prev_select = $sel.val();
	if (res.length > 0) {
        	prev_top = res[0].id;
	}

        var html = $.templates('#battle-template').render(res.map(function(x){
            d = new Date(x._creation_date);
            r = x.body;
            r.date = d.toLocaleString('ru', {month: '2-digit', day: '2-digit', hour: '2-digit', minute:'2-digit'})
            return r;
        }));
        $('#battles-list').html(html);

        /*
    $.post('get_results', function(data) {
        var html = $.templates('#result-template').render(data);
        $('#results').html(html);
        for (i in data) {
            if (data[i].name == USERNAME) {
                $('#user_name').html(USERNAME + ' [№' + i + ' ~' + data[i].mean.toFixed(2) + ']');
            }
        }
    });
    */
    }).fail(function(error) {
        console.log("error ", error);
    });
}

function getVersions() {
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
}

function getResults(show_all) {
    var x;
    if (show_all) {
        x = 'true';
    } else {
        x = 'false';
    }
    $.post('get_results2', {'show_all': x}, function(data) {
        console.log('x', data);
        var head = $.templates('#result-templateh').render(data.slice(0, 1));
        var tab = $.templates('#result-template2').render(data.slice(1));
        $('#results').html(head + tab);
        //for (i in data) {
        //    if (data[i].name == username) {
        //        $('#user_name').html(username + ' [№' + i + ' , wins: ' + data[i].wins + ']');
        //    }
        //}
    });
}

function logged(username) {
    USERNAME = username;
    console.log("logged ", username);
    $('#user_name').html('Hi ' + username);
    $('#up_login').hide();
    $('#up_logged').show();

    getVersions();

    $('#battles-select').change();

    /*
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
    */

    getResults(false);
    //setInterval(battlesSelect, 5000);
}

$(document).ready(function() {
    pleer = new Pleer(800, 600);

    BaasBox.fetchCurrentUser()
        .done(function(res) {
            $('#box').css('visibility', 'visible');
            logged(res.data.user.name);
        })
        .fail(function(error) {
            window.location.replace('/login');
            console.log("error1 ", error);
            $('#up_login').show()
        });

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
        $('#loading').text('... loading ...');
        $('#upload_form>input').prop('disabled', true);
        BaasBox.uploadFile(formData).done(function(res) {
            console.log("res ", JSON.parse(res));
            console.log(JSON.parse(res).data.id);
            $('#upload_form>input').prop('disabled', false);
            $('#loading').text('... done, 2min timeout for next upload ...');
            setTimeout(function() {
                $('#upload_form>input').prop('disabled', false);
            }, 120000);
            getVersions();
        }).fail(function(error) {
            $('#loading').text('... error ...');
            $('#upload_form>input').prop('disabled', false);
            console.log("error ", error);
        })
    });
    $("#battle_form").submit(function(e) {
        e.preventDefault();
        var formObj = $(this);
        var formData = new FormData(this);
        console.log($(this).serialize());
        $('#battle_form>input').prop('disabled', true);
        $.post('battle', $(this).serialize(), function(data) {
            console.log(data);
        });
        setTimeout(function() {
            $('#battle_form>input').prop('disabled', false);
        }, 300000);
        alert('timeout 5min to create next battle');
        alert('Запрос на бой отправлен. Подождите, он скоро появится в списке боев. И не надо еще раз нажимать на кнопку.');
    });
    $("#battles-form").submit(function(e) {
        e.preventDefault();
        console.log($(this).serialize());
        battlesSelect($('#user1').val(), $('#user2').val())
    });
    $("#pleer-toggle").click(function() { pleer.toggle() });
    $('#pleer-pos').change(function() { pleer.jump(parseInt($(this).val())); });
    $('#pleer-pos').mousedown(function() { pleer.freeze(); });
    $('#pleer-pos').mouseup(function() { pleer.unfreeze(); });
    $('#battles-select').change(battlesSelect);
    $('#btn-switch').click(function() {
        $('#btn-switch').prop('disabled', true);
        cur_show_all = !cur_show_all;
        getResults(cur_show_all);
        if (cur_show_all) {
            $('#btn-switch').text('не показывать участников вне конкурса');
        } else {
            $('#btn-switch').text('показать участников вне конкруса');
        }
        $('#btn-switch').prop('disabled', false);
    })
});
