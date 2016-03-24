odoo.define('theme_weche.snippet_fbpost_opt', function(require) {
    "use strict"

    var s_options = require('web_editor.snippets.options');

    s_options.registry.js_fb_post_link = s_options.Class.extend({
        focus: function() {
            var fb_posturl = prompt("Посилання на пост ФБ");
            if (fb_posturl != null) {
                this.$target.find('.fb-post').attr('data-href', fb_posturl);
            }
        },
        start: function() {
            var def_url = "https://www.facebook.com/20531316728/posts/10154009990506729/";
            var fb_posturl = this.$target.find('.fb-post').attr('data-href');
            if (fb_posturl == def_url) {
                var new_url = prompt("Посилання на пост ФБ");
                if (new_url != null) {
                    this.$target.find('.fb-post').attr('data-href', new_url);
                }
            }
        }
    });

    s_options.registry.js_tw_post_link = s_options.Class.extend({
        focus: function() {
            var tw_id = prompt("Твіт ID");
            var tweet = this.$target.find(".tweet");
            if (tw_id != null && tweet != null) {
                tweet.attr('tweetID', tw_id);
                // twttr.widgets.createTweet(
                //     tw_id,
                //     tweet[0], {
                //         conversation : 'all',
                //         cards        : 'visible',
                //         linkColor    : '#A31621',
                //         theme        : 'light'
                //     }
                // );
            }
        },
        start: function() {
            var tw_id = prompt("Твіт ID");
            var tweet = this.$target.find(".tweet");
            if (tw_id != null && tweet != null) {
                tweet.attr('tweetID', tw_id);
                // twttr.widgets.createTweet(
                //     tw_id,
                //     tweet[0], {
                //         conversation : 'all',
                //         cards        : 'visible',
                //         linkColor    : '#A31621',
                //         theme        : 'light'
                //     }
                // );
            }
        },
    });

});
