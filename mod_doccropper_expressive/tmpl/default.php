<?php
/** @var Joomla\CMS\Helper\ModuleHelper $module */
/** @var Joomla\Registry\Registry $params */

defined('_JEXEC') or die;

$exportEndpoint = $params->get('endpoint_export', '/api/export');
$downloadEndpoint = $params->get('endpoint_download', '/api/export/download');
$signEndpoint = $params->get('endpoint_sign', '/api/sign');
?>
<div x-data="{drawer:false, tab:'export', exporting:false, showModal:false, toast:''}"
     x-on:dc-exported.window="showModal = true; toast='Export completed'; setTimeout(()=>toast='',3000)">
  <?php require __DIR__ . '/partials/appbar.php'; ?>
  <?php require __DIR__ . '/partials/main.php'; ?>
  <?php require __DIR__ . '/partials/modals.php'; ?>
  <?php require __DIR__ . '/partials/toasts.php'; ?>
  <script>
    window.DC_EXPORT_ENDPOINT = <?php echo json_encode($exportEndpoint); ?>;
    window.DC_DOWNLOAD_ENDPOINT = <?php echo json_encode($downloadEndpoint); ?>;
    window.DC_SIGN_ENDPOINT = <?php echo json_encode($signEndpoint); ?>;
    window.DC_CSRF = '<?php echo $token; ?>';
  </script>
</div>
