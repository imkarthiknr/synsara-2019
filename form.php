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
	<form id="reg" action="register1.php" method="post" onsubmit="return checkForm(this);">
          <!-- <div class="floating-logo">
            <a href="index.html"><img src="img/plogo2k15.png" alt="paradigm-logo" width="100%"/></a>
          </div> -->
        <div class="hide">
          <div class="top_bar" ></div>
        <div class="h_register">
          <div class= "reg-title">REGISTRATION<br><p>&diams; &diams; &diams;</p></div> <br>
            <div class="form">
            Name:<br /><input class="name" name="name" type="text" required /><br /><br />
            College:<br /> <input class="college" name="college" type="text" required /><br /> <br />
            <div class="dept"> Department:<br /><input class="department" name="dept" list='dept-list' required />
              <datalist id="dept-list">
                <option value="CSE" />
                <option value="IT" />
                <option value="ECE" />
				<option value="EEE" />
				<option value="MECH" />
				<option value="EIE" />
				<option value="CIVIL" />
				<option value="ICE" />
				<option value="EIE" />
              </datalist>
            </div>
            <div class="yr"> Year:<br /><input class="year" name="yr" list="yr-list" required />
              <datalist id="yr-list">
                <option value="I"/>
                <option value="II"/>
                <option value="III"/>
                <option value="IV"/>
              </datalist><br />
            </div>
            <br /><br /><br />E-mail:<br /><input class="email" name="email" type="email" required />
            <br /><br />Mobile:<br /><input class="mobile" name="mobile" required type="text" pattern="[6789][0-9]{9}" title="Phone number with 6-9 and remaing 9 digit with 0-9" /><br /> <br />
          </div>
          <br />
          <div class="submit_block">
          <input type="submit" value="REGISTER" class="submit" />
          </div>
        </div>
        </div>
	</form>
  </body>
</html>
