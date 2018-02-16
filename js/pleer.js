function Pleer(width, height) {
    this.app = new PIXI.Application(800, 600, {backgroundColor : 0x0});
    $('#pleer').append(this.app.view);


    this.frozen = false;
    this.running = false;
    this.app.ticker.stop();
    this.app.ticker.add(function(delta) {
                            if (!this.frozen) {
                                $('#pleer-pos').val(this.cur_frame);
                            }
                            this.text_frame.text = this.cur_frame.toString();
                            this.setFrame(this.frames[this.cur_frame]);
                            if (this.running) {
                                if (this.cur_frame < this.frames.length - 1) {
                                    this.cur_frame += 1;
                                } else {
                                    this.running = false;
                                }
                                that = this;
                                ms = 60  - this.app.ticker.elapsedMS;
                                if (ms <= 0) {
                                    setTimeout(function() {
                                        that.app.ticker.update();
                                    }, 0);
                                } else {
                                    setTimeout(function() {
                                        that.app.ticker.update();
                                    }, 80 - ms);
                                }
                            }
                        }, this);
    this.bullets = [];
    this.tanks = [];
    this.text = [];
    this.text_frame = new PIXI.Text('', {fill: 0xFFFFFF});
    this.text_frame.x = 700;
    this.text_frame.y = 550;
    this.app.stage.addChild(this.text_frame);

    var tank_colors = [0xee5555, 0x55ee55];

    for (var i = 0; i < 2; i++) {
        var gr = new PIXI.Graphics();
        gr.beginFill(tank_colors[i]);
        gr.drawCircle(0, 0, 15);
        gr.endFill();
        this.tanks.push(gr);
        this.app.stage.addChild(gr);

        var te = new PIXI.Text('', {fill: tank_colors[i]});
        te.x = 30;
        te.y = 30 + i * 30;
        this.text.push(te);
        this.app.stage.addChild(te);
    }

    this.setFrame = function(frame) {
        if ('error' in frame) {
            this.text[0].text = '';
            this.text[1].text = frame['error'];
            return;
        }

        if (this.tanks.length != frame.tanks.length) {
            if (frame.tanks.length == 1) {
                deleted = 1 - frame.tanks[0].ind;
                this.text[deleted].text = this.tanks[deleted].name + ' destroyed';
            } else {
                throw "tanks arrays of different lengths";
            }
        }

        for (var i = 0; i < frame.tanks.length; i++) {
            ind = frame.tanks[i].ind;
            this.tanks[ind].x = frame.tanks[i].pos[0];
            this.tanks[ind].y = frame.tanks[i].pos[1];
            this.tanks[ind].name = frame.tanks[i].name;
            this.text[ind].text = frame.tanks[i].name + ' ' + frame.tanks[i].health;
        }

        if (this.bullets.length < frame.bullets.length) {
            for (var i = this.bullets.length; i < frame.bullets.length; i++) {
                var gr = new PIXI.Graphics();
                gr.beginFill(0xeeeeee);
                gr.drawCircle(0, 0, 3);
                gr.endFill();
                this.bullets.push(gr);
                this.app.stage.addChild(gr);
            }
        } else if (this.bullets.length > frame.bullets.length) {
            for (var i = frame.bullets.length; i < this.bullets.length; i++) {
                this.app.stage.removeChild(this.bullets[i]);
            }
            this.bullets.splice(frame.bullets.length, this.bullets.length - frame.bullets.length);
        }
        for (var i = 0; i < frame.bullets.length; i++) {
            this.bullets[i].x = frame.bullets[i].pos[0];
            this.bullets[i].y = frame.bullets[i].pos[1];
        }

    }

    this.play = function(frames) {
        this.frames = frames;
        $('#pleer-pos').attr('min', 0);
        $('#pleer-pos').attr('max', frames.length - 1);
        this.cur_frame = 0;
        //if (!this.app.ticker.started)
        //    this.app.ticker.start();
        if (!this.running) {
            this.running = true;
            this.app.ticker.update();
        }
    }

    this.toggle = function() {
        if (this.running)
            //this.app.ticker.stop();
            this.running = false;
        else {
            if (this.cur_frame < this.frames.length - 1) {
                this.cur_frame += 1;
            }
            //this.app.ticker.start();
            this.running = true;
        }
    }

    this.jump = function(ind) {
        this.cur_frame = ind;
        this.app.ticker.update();
    }

    this.freeze = function() {
        this.frozen = true;
    }

    this.unfreeze = function() {
        this.frozen = false;
    }
}
