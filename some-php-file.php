<?php

use App\ModelMigrated\userModel;

/**
 * Class defaultModel
 *
 * Handles default model actions related to content items management.
 */
class defaultModel
{
    // ------------------------------------
    // Core functionality
    // ------------------------------------
    
    /**
     * Processes POST actions for content item configuration
     * 
     * @global object $translate Translation object (unused in current implementation)
     * @global object $auth Authentication object
     * 
     * @return bool Returns false if no action processed
     * @throws \Exception Potential database exception from userModel::update_user
     */
    static function check_action()
    {
        global $translate, $auth;
        if (isset($_POST['action'])) {
            switch ($_POST['action']) {
                // ------------------------------------
                // Set content items case
                // ------------------------------------
                /**
                 * Handles setting content items based on POST data.
                 * Updates the user's default content items and saves them to the database.
                 */
                case 'set_content_items':
                    // xxxx Controller::init_site_model('user');
                    $my_items = $auth->getIdentity()->default_content_items;
                    $new_items = array();
                    if (isset($_POST['active']) && count($_POST['active']) > 0) {
                        foreach ($_POST['active'] as $item) {
                            $size = 12;
                            if (isset($_POST['size'][$item]))
                                $size = (int)$_POST['size'][$item];
                            $new_items[$item]['bl'] = $size;
                            $pos = 999;
                            if (isset($my_items[$item]['pos']))
                                $pos = (int)$my_items[$item]['pos'];
                            $new_items[$item]['pos'] = $pos;
                        }
                    }
                    $id = $auth->getIdentity();
                    \App\Misc\View::aasort($new_items, 'pos');
                    $id->default_content_items = $new_items;
                    userModel::update_user($auth->getIdentity()->user_id, array('default_content_items' => base64_encode(gzcompress(serialize($new_items)))));
                    echo json_encode(true);
                    die();
                    break;

                // ------------------------------------
                // Sort content items case
                // ------------------------------------
                /**
                 * Handles sorting content items based on POST data.
                 * Updates the position of content items and saves the new order to the database.
                 */
                case 'sort_content_items':
                    // xxxx Controller::init_site_model('user');
                    $my_items = $auth->getIdentity()->default_content_items;
                    if (isset($_POST['content_ids']) && count($_POST['content_ids']) > 0) {
                        foreach ($_POST['content_ids'] as $key => $item) {
                            if (isset($my_items[$item]['pos']))
                                $my_items[$item]['pos'] = $key;
                        }
                        $id = $auth->getIdentity();
                        \App\Misc\View::aasort($my_items, 'pos');
                        $id->default_content_items = $my_items;
                        userModel::update_user($auth->getIdentity()->user_id, array('default_content_items' => base64_encode(gzcompress(serialize($my_items)))));
                    }
                    
                    echo json_encode(true);
                    die();
                    break;
            }
        }
        return false;
    }
}