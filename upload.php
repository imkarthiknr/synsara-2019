<?php
//Include PHPExcel
require_once 'Classes/PHPExcel.php';
require_once 'Classes/PHPExcel/IOFactory.php';
require_once 'config.php';

$error = '';
function clean_text($string)
{
 $string = trim($string);
 $string = stripslashes($string);
 $string = htmlspecialchars($string);
 return $string;
}

function create_file($path,$name,$email,$dept,$college,$yr,$mobile,$regtime)
{
    //echo"thiru";
  $objPHPExcel = new PHPExcel();
  if(file_exists($path))
  {
    $objPHPExcel = PHPExcel_IOFactory::load($path);
  }
  //echo"thiru2";
    $objPHPExcel->setActiveSheetIndex(0);
  $row = $objPHPExcel->getActiveSheet()->getHighestRow();
  if($row == 1)
  {
    ////// style/////////////
    $objPHPExcel->getDefaultStyle()->getFont()->setName('Arial')->setSize(15);
    $objPHPExcel->getActiveSheet()->SetCellValue('A'.$row, 'ID');
    $objPHPExcel->getActiveSheet()->SetCellValue('B'.$row, 'Name');
    $objPHPExcel->getActiveSheet()->SetCellValue('C'.$row, 'College');
    $objPHPExcel->getActiveSheet()->SetCellValue('D'.$row, 'Department');
    $objPHPExcel->getActiveSheet()->SetCellValue('E'.$row, 'Year');
    $objPHPExcel->getActiveSheet()->SetCellValue('F'.$row, 'Email');
    $objPHPExcel->getActiveSheet()->SetCellValue('G'.$row, 'Mobile');
    $objPHPExcel->getActiveSheet()->SetCellValue('H'.$row, 'RegTime');
  }
  $id = $row;
  $row = $row+1;
  //echo"thiru3333";
  ////// style/////////////
  $objPHPExcel->getDefaultStyle()->getFont()->setName('Arial')->setSize(10);
  $objPHPExcel->getActiveSheet()->SetCellValue('A'.$row, $id);
  $objPHPExcel->getActiveSheet()->getColumnDimension('A')->setWidth(10);
  $objPHPExcel->getActiveSheet()->SetCellValue('B'.$row, $name);
  $objPHPExcel->getActiveSheet()->getColumnDimension('B')->setWidth(30);
  $objPHPExcel->getActiveSheet()->SetCellValue('C'.$row, $college);
  $objPHPExcel->getActiveSheet()->getColumnDimension('C')->setWidth(30);
  $objPHPExcel->getActiveSheet()->SetCellValue('D'.$row, $dept);
  $objPHPExcel->getActiveSheet()->getColumnDimension('D')->setWidth(10);
  $objPHPExcel->getActiveSheet()->SetCellValue('E'.$row, $yr);
  $objPHPExcel->getActiveSheet()->getColumnDimension('E')->setWidth(10);
  $objPHPExcel->getActiveSheet()->SetCellValue('F'.$row, $email);
  $objPHPExcel->getActiveSheet()->getColumnDimension('F')->setWidth(30);
  $objPHPExcel->getActiveSheet()->SetCellValue('G'.$row, $mobile);
  $objPHPExcel->getActiveSheet()->getColumnDimension('G')->setWidth(15);
  $objPHPExcel->getActiveSheet()->SetCellValue('H'.$row, $regtime);
  $objPHPExcel->getActiveSheet()->getColumnDimension('H')->setWidth(40);
  //echo"thiru44444";
  $objWriter = new PHPExcel_Writer_Excel2007($objPHPExcel);
  //echo"thiru55555";
  $objWriter->save($path);
  //echo "karu";
  return $id;
}

function create_specific_file($path,$id,$name,$email,$dept,$college,$yr,$mobile,$regtime)
{
  $objPHPExcel = new PHPExcel();
  if(file_exists($path))
  {
    $objPHPExcel = PHPExcel_IOFactory::load($path);
  }
  $objPHPExcel->setActiveSheetIndex(0);
  $row = $objPHPExcel->getActiveSheet()->getHighestRow();
  if($row == 1)
  {
    ////// style/////////////
    $objPHPExcel->getDefaultStyle()->getFont()->setName('Arial')->setSize(15);
    $objPHPExcel->getActiveSheet()->SetCellValue('A'.$row, 'ID');
    $objPHPExcel->getActiveSheet()->SetCellValue('B'.$row, 'Name');
    $objPHPExcel->getActiveSheet()->SetCellValue('C'.$row, 'College');
    $objPHPExcel->getActiveSheet()->SetCellValue('D'.$row, 'Department');
    $objPHPExcel->getActiveSheet()->SetCellValue('E'.$row, 'Year');
    $objPHPExcel->getActiveSheet()->SetCellValue('F'.$row, 'Email');
    $objPHPExcel->getActiveSheet()->SetCellValue('G'.$row, 'Mobile');
    $objPHPExcel->getActiveSheet()->SetCellValue('H'.$row, 'RegTime');
  }
  $row = $row+1;
  ////// style/////////////
  $objPHPExcel->getDefaultStyle()->getFont()->setName('Arial')->setSize(10);
  $objPHPExcel->getActiveSheet()->SetCellValue('A'.$row, $id);
  $objPHPExcel->getActiveSheet()->getColumnDimension('A')->setWidth(10);
  $objPHPExcel->getActiveSheet()->SetCellValue('B'.$row, $name);
  $objPHPExcel->getActiveSheet()->getColumnDimension('B')->setWidth(30);
  $objPHPExcel->getActiveSheet()->SetCellValue('C'.$row, $college);
  $objPHPExcel->getActiveSheet()->getColumnDimension('C')->setWidth(30);
  $objPHPExcel->getActiveSheet()->SetCellValue('D'.$row, $dept);
  $objPHPExcel->getActiveSheet()->getColumnDimension('D')->setWidth(10);
  $objPHPExcel->getActiveSheet()->SetCellValue('E'.$row, $yr);
  $objPHPExcel->getActiveSheet()->getColumnDimension('E')->setWidth(10);
  $objPHPExcel->getActiveSheet()->SetCellValue('F'.$row, $email);
  $objPHPExcel->getActiveSheet()->getColumnDimension('F')->setWidth(30);
  $objPHPExcel->getActiveSheet()->SetCellValue('G'.$row, $mobile);
  $objPHPExcel->getActiveSheet()->getColumnDimension('G')->setWidth(15);
  $objPHPExcel->getActiveSheet()->SetCellValue('H'.$row, $regtime);
  $objPHPExcel->getActiveSheet()->getColumnDimension('H')->setWidth(40);
  $objWriter = new PHPExcel_Writer_Excel2007($objPHPExcel);
  $objWriter->save($path);
  return $row-1;
}

if($_SERVER["REQUEST_METHOD"] == "POST")
{
  $regtime=$_POST["regtime"];
  $sql = "SELECT * FROM details WHERE email = ?";
  //echo $sql;
  if($stmt = mysqli_prepare($link, $sql))
  {
    // Bind variables to the prepared statement as parameters
    //echo "statement created";
    mysqli_stmt_bind_param($stmt, "s", $email);           
    // Attempt to execute the prepared statement
    if(mysqli_stmt_execute($stmt))
    {
      //store result 
      //echo "Hi";
      mysqli_stmt_store_result($stmt);                
      if(mysqli_stmt_num_rows($stmt) >= 1)
      {
        header("location: errorpages/500.html");            
      }
      else
      {
        // writing in excel file
        //echo "Hi";
        $path = "downloads\\total.xlsx";
        $id = create_file($path,$name,$email,$dept,$college,$yr,$mobile,$regtime);
        //echo $path." ".$id."</br>";
        if(!empty($_POST['TechEvent']))
        {
            //echo "Hi";
          foreach($_POST['TechEvent'] as $selected)
          {
            $path = "downloads\\".$selected.".xlsx";
            $row = create_specific_file($path,$id,$name,$email,$dept,$college,$yr,$mobile,$regtime);
            //echo $path." ".$row."</br>";
          }
        }

        if(!empty($_POST['NonTechEvent']))
        {
            //echo "Hi";
          foreach($_POST['NonTechEvent'] as $selected)
          {
            $path = "downloads\\".$selected.".xlsx";
            $row = create_specific_file($path,$id,$name,$email,$dept,$college,$yr,$mobile,$regtime);
            //echo $path." ".$row."</br>";
          }
        }
        // Prepare an insert statement
        $sql = "INSERT INTO details (email, mobile, name, dept, clg, year,regtime) VALUES (?,?,?,?,?,?,?)";   
        if($stmt1 = mysqli_prepare($link, $sql))
        {
            // Bind variables to the prepared statement as parameters
            mysqli_stmt_bind_param($stmt1,"sssssss", $email, $mobile, $name, $dept, $college, $yr, $regtime);            
            if($res = mysqli_stmt_execute($stmt1))
            {
              // Redirect to login page
              // Close statement
              mysqli_stmt_close($stmt1);
              // sent mail
              /*$to = $email;
              echo $to;
              $subject = "My subject";
              $txt = "Hello world!";
              $headers = "From: synsara2k19@example.com" . "\r\n" .
              "CC: somebodyelse@example.com";
              mail($to,$subject,$txt,$headers);*/
              header("location: final.php");  
            } 
            else
            {
                echo "ERROR in Insert stt: Something went wrong. Please try again later : ".mysqli_stmt_error($stmt1);
            }
        }
        // Close statement
        mysqli_stmt_close($stmt1);
      }
    }
    // Close statement
    mysqli_stmt_close($stmt);
  }
// Close connection
  mysqli_close($link);
}
?>