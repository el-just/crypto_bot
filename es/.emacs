(add-to-list 'custom-theme-load-path "~/.emacs.d/themes/")

(add-to-list 'load-path "~/.emacs.d/el-get/el-get")
(unless (require 'el-get nil t)
  (url-retrieve
   "https://github.com/dimitri/el-get/raw/master/el-get-install.el"
   (lambda (s)
     (end-of-buffer)
     (eval-print-last-sexp))))

(add-to-list 'el-get-recipe-path "~/.emacs.d/el-get-user/recipes")
(el-get 'sync)

(load-theme 'zenburn t)
(setq-default cursor-type 'bar)
(scroll-bar-mode -1)
(menu-bar-mode -1)
(tool-bar-mode -1)
(set-face-attribute 'default nil :height 138
(add-to-list 'default-frame-alist '(fullscreen . maximized)))