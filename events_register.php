<!doctype html>
<html class="no-js" lang="">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="x-ua-compatible" content="ie=edge">
        <title>Registration | SYNSARA 2K19</title>
        <meta name="description" content="">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <meta name="theme-color" content="#cd2929">
        <meta name="mobile-web-app-capable" content="yes"/>

        <link rel="apple-touch-icon" href="img/plogo2k15.png">
        <link rel="shortcut icon" href="img/plogo2k15.png" type="image/x-icon" />
        <!-- Place favicon.ico in the root directory -->

        <link rel="stylesheet" href="css/normalize.css">
        <link rel="stylesheet" href="css/styler.css">
    </head>
    <body>
<?php
$name = trim($_GET["name"]);
$email = trim($_GET["email"]);
$college = trim($_GET["college"]);
$dept = trim($_GET["dept"]);
$yr = trim($_GET["year"]);
$mobile = trim($_GET["mobile"]);
//echo  $name.$email.$college.$dept.$yr.$mobile;
if($_SERVER["REQUEST_METHOD"] == "POST")
{
	///// updating in excel files..........
	require_once 'upload.php';
}
$date = new DateTime(); 
$dt=$date->format('Y-m-d H:i:s');
?>			
<form id="reg" method="post">
    <!-- <div class="floating-logo">
        <a href="index.html"><img src="img/plogo2k15.png" alt="paradigm-logo" width="100%"/></a>
    </div> -->
    <div class="hide">
	<div class="top_bar" ></div>
    <div class="h_register">
      <div class= "reg-title">EVENT REGISTRATION<br><p>&diams; &diams; &diams;</p></div><br />
	  <div class="form" >
        <table width="100%"><td style="color:red">
		Name: </td><td><?php echo $name; ?></td></tr>
        <tr><td style="color:red">College: </td><td><?php echo $college; ?></td><td style="color:red">Department: </td><td><?php echo $dept; ?> &nbsp&nbsp&nbsp&nbsp&nbsp <span style="color:red">Year:</span> &nbsp <?php echo $yr; ?></td></tr>
        <tr><td style="color:red">E-mail: </td><td><?php echo $email; ?></td><td style="color:red">Mobile: </td><td><?php echo $mobile; ?></td></tr>
      </table>
	  </div>
	  <hr style="height:1px;border:none;color:#333;background-color:#333;" />
	  <marquee behavior="scroll" direction="left" class="form2">on participating in Hackathon, you cannot participate in other events.</marquee>
	  <div id="techblock">
	  <div class="form3"><b>Technical Events(can participate only in any two)<br /> </b></div>
	  <div class="form2"><input type="checkbox" name="TechEvent[]" value="Code Fest" />&nbsp Code Fest <br />
	  <input type="checkbox" name="TechEvent[]" value="Code Relley" />&nbsp Code Relley <br />
	  <input type="checkbox" name="TechEvent[]" value="Paper Presentation" />&nbsp Paper Presentation <br />
	  &nbsp need to add fileupload for onselect...<br />
	  <input type="checkbox" name="TechEvent[]" value="event 4" />&nbsp event 4 <br />
	  <input type="checkbox" name="TechEvent[]" value="event 5" />&nbsp event 5 <br /><br /></div></div>
	  <div id="nontechblock">
	  <div class="form3"><b>Non-Technical Events(can participate only in any two)<br /></b></div>
	  <div class="form2"><input type="checkbox" name="NonTechEvent[]" value="non tech event 1" />&nbsp non tech event 1 <br />
	  <input type="checkbox" name="NonTechEvent[]" value="non tech event 2" />&nbsp non tech event 2 <br />
	  <input type="checkbox" name="NonTechEvent[]" value="non tech event 3" />&nbsp non tech event 3 <br /></div></div>
	  <input type="hidden" name="regtime" value="<?php echo $dt ?>" />
      <div class="submit_block">
          <input type="submit" value="REGISTER" class="submit" name="submit" />
      </div>
	  </div>
	  </div>
    </div>
</form>		
</body>
</html>
