<?php

/*  onsite web mySql credentials
        $servername = "www.karthikproject.biz";
        $username = "karthikproject";
        $password = "Karthik@1999";
        $dbname = "karthikp_BlogSpot";
		$dbConnection = mysqli_connect($servername, $username, $password, $dbname);

*/
define('DB_SERVER', 'localhost');
define('DB_USERNAME', 'root');
define('DB_PASSWORD', '');
define('DB_NAME', 'synsara');
 
/* Attempt to connect to MySQL database */
$link = mysqli_connect(DB_SERVER, DB_USERNAME, DB_PASSWORD, DB_NAME);
 
// Check connection
if($link === false){
    die("ERROR: Could not connect. " . mysqli_connect_error());
}else{
	//echo "DB connected";
}
?>