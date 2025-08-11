<?php
defined('_JEXEC') or die;

JHtml::_('script', 'https://cdn.tailwindcss.com', ['version' => 'auto']);
JHtml::_('script', 'https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js', ['version' => 'auto', 'defer' => true]);
JHtml::_('script', 'media/doccropper/js/doccropper.adapter.js', ['version' => 'auto'], ['defer' => true]);

JHtml::_('behavior.core');
$token = JSession::getFormToken();

require JModuleHelper::getLayoutPath('mod_doccropper_expressive', $params->get('layout', 'default'));
