odoo.define('theme_weche.website_blog_inh', function(require) {
    "use strict";

    var blog = require('website_blog.website_blog');
    // temp fix
    // remove style set by original website_blog.js:45
    $(document).ready(function() {
        if ($('.website_blog').length) {
            if ($('#js_blogcover').length) {
                $('#js_blogcover[style*="background-image: url"]').css('min-height', '');
            }
        }

    });
});
