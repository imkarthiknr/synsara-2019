<?php

//var_dump($_POST);
require_once "config.php";

if($_SERVER["REQUEST_METHOD"] == "POST")
{
    $email = '';
    $mobile = '';
    $email_err = '';
    $mobile_err = '';

    // Validate email
    if(empty(trim($_POST["email"]))){
        $email_err = "Please enter a email.";     
    } else{
        $email = trim($_POST["email"]);
    }
    
    // Validate mobile
    if(empty(trim($_POST["mobile"])))
    {
        $mobile_err = "Please enter mobile.";     
    } else{
        $mobile = trim($_POST["mobile"]);
    }
    $sql = "SELECT * FROM details WHERE email = ?";
    //echo $sql;
    if($stmt = mysqli_prepare($link, $sql)){
        // Bind variables to the prepared statement as parameters
        //echo "statement created";
        mysqli_stmt_bind_param($stmt, "s", $email);           
        // Attempt to execute the prepared statement
        if(mysqli_stmt_execute($stmt)){
            //store result 
            mysqli_stmt_store_result($stmt);                
            if(mysqli_stmt_num_rows($stmt) >= 1){
                header("location: errorpages/500.html");            
            } else{
                $name = $_POST["name"];
				$college = $_POST["college"];
				$dept = $_POST["dept"];
				$yr = $_POST["yr"];
				//echo $name." - ".$college." - ".$dept." - ".$yr;
                header("location: events_register.php?name=$name&college=$college&dept=$dept&year=$yr&email=$email&mobile=$mobile");
            }
        } else{
            echo "ERROR in e-mail: Oops! Something went wrong. Please try again later.";
        }
    }
	// Close statement
	mysqli_stmt_close($stmt);
    
    /*// Check input errors before inserting in database
    if(empty($username_err) && empty($email_err) && empty($mobile_err))
    {
        // Prepare an insert statement
        $sql = "INSERT INTO details (email, mobile) VALUES (?,?)";    
		
        if($stmt = mysqli_prepare($link, $sql)){
            // Bind variables to the prepared statement as parameters
            mysqli_stmt_bind_param($stmt,"ss", $email, $mobile);            
            // Set parameters
            $param_username = $username;
            //$param_password = password_hash($password, PASSWORD_DEFAULT); // Creates a password hash            
            // Attempt to execute the prepared statement
            if($res = mysqli_stmt_execute($stmt)){
                // Redirect to login page
                
            } else{
                echo "ERROR in Insert stt: Something went wrong. Please try again later : ".mysqli_stmt_error($stmt);
            }
        }
        // Close statement
        mysqli_stmt_close($stmt);
    }else {
		echo "ERROR : ".$username_err." - ".$email_err." - ".$mobile_err;
    }*/
    // Close connection
    mysqli_close($link);
}

?>