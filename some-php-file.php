<?php

use App\ModelMigrated\userModel;

/**
 * Class defaultModel
 *
 * This class handles default model operations, particularly related to content items.
 */
class defaultModel
{
    // ----
    // Action Handling Section
    // ----

    /**
     * Checks and processes actions based on POST data.
     *
     * This method handles two primary actions:
     * - 'set_content_items': Updates the default content items for the authenticated user.
     * - 'sort_content_items': Sorts the default content items based on the provided order.
     *
     * @global object $translate Translation object
     * @global object $auth Authentication object
     *
     * @return bool Returns false if no action is processed, otherwise terminates with JSON response.
     */
    static function check_action()
    {
        global $translate, $auth;
        if (isset($_POST['action'])) {
            switch ($_POST['action']) {
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