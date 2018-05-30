export function AccountSettingsController(AppApi, UserAccounts, $location, $mdDialog ,$stateParams, $mdToast, $state) {
  console.log($stateParams.accountId)
  var $ctrl = this;
	$ctrl.api_key;
	$ctrl.team_url;
    $ctrl.userAccounts = UserAccounts;
    $ctrl.integration_id = $stateParams.accountId
    $ctrl.submitForm = function(){
//        $ctrl.isDisabled = true;
//        console.log($ctrl.accountDetails.AWS_APIAccessKey)
//                                console.log($ctrl.accountDetails.AWS_APISecretAccess)
//                                console.log($ctrl.integration_id)
//                                console.log("aasdfghjkzxcvbnm")

		AppApi.submitForm({
//
		                        'AZURE_tenant_id': $ctrl.accountDetails.AZURE_tenant_id,
                                'AZURE_client_id': $ctrl.accountDetails.AZURE_client_id,
                                'AZURE_subscription_id' :  $ctrl.accountDetails.AZURE_subscription_id,
                                'AZURE_client_secret' : $ctrl.accountDetails.AZURE_client_secret,
                                'user_integration_id': $stateParams.accountId,
                                'AZURE_update_login_flag' : $ctrl.accountDetails.AZURE_update_login_flag,


									})
									.then(function(response){
									if(response.status==200){
									    $ctrl.showSimpleToast(response.data);
									    $ctrl.isDisabled = false;}
	                                else{
	                                    $ctrl.returned = "Something went wrong, try again later";
	                                    $ctrl.isDisabled = false;
	                                    }
	                                 });
	}

//	$ctrl.submitSettings = function(){
//	    AppApi.submitSettings({
//	                            'new_ticket_notification': $ctrl.accountDetails.notification,
//	                            'integration_id': $ctrl.integration_id,}).then(function(response){
//									if(response.status==200){
//									    $ctrl.showSimpleToast(response.data);
//									    }
//	                                else{
//	                                    $ctrl.returned = "Something went wrong, try again later";
//
//	                                    }
//	                                 });
//	}

    $ctrl.goBack = function(){
        $state.go('accountList')
    }

    $ctrl.newUrl = function(){
        AppApi.newUrl({'integration_id':$ctrl.integration_id})
            .then(function(result){
//                console.log(result)
                $ctrl.accountDetails.callback = result.data.callback;
            });
    }

    $ctrl.$onInit = function() {
        AppApi.getUserAccount($stateParams.accountId)
        .then(function (result) {
            $ctrl.userAccounts = result.data;
           console.log($ctrl.userAccounts.is_valid);
        });
      }

    $ctrl.deleteaccount = function() {

    console.log("till here")
    AppApi.deleteUserAccount($stateParams.accountId)

    }


  $ctrl.showSimpleToast = function(data) {
    $mdToast.show(
                     $mdToast.simple()
                        .textContent(data)
                        .hideDelay(10000)
                  )};

}
