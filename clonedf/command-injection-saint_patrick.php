<?php

function process_order($item) {
    $temp_dirname = "/tmp/".uniqid();
    mkdir($temp_dirname);

    $log_file = "$temp_dirname/orders.log";
    file_put_contents($log_file, "Order received: " . $item . "\n", FILE_APPEND);
    
    return generate_order_ticket($item, $temp_dirname);
}

function generate_order_ticket($item, $dirname) {
    // Escaping to avoid command injection :)
    $safe_item = escapeshellcmd($item);
    $current_time = time();

    $archive_name = "/tmp/".$current_time."_".$safe_item.".gz";

    $cmd = "cd $dirname; tar -cf $archive_name .";
    $output = shell_exec($cmd);

    return "[INFO] " . htmlspecialchars($output ?? "Order processed");
}

$items = [
    "beer" => "Pint of beer 🍺",
    "hat" => "Leprechaun hat 🎩",
    "clover" => "Four-leaf clover 🍀",
    "gold" => "Gold coin 🏅"
];

if ($_SERVER["REQUEST_METHOD"] === "POST" && isset($_POST['item'])) {
    $order_result = process_order($_POST['item']);
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Saint-Patrick Black Market</title>
    <link rel="stylesheet" href="/ignore/design/style.css">
</head>
<body>
    <div class="terminal">
        <header>
            <h1>Saint-Patrick Black Market 🍀</h1>
            <p>Underground Shop</p>
        </header>
        
        <main>
            <p>Select an item:</p>
            <form method="POST">
                <div class="dropdown">
                    <select name="item">
                        <?php foreach ($items as $key => $name): ?>
                            <option value="<?php echo htmlspecialchars($key); ?>"><?php echo $name; ?></option>
                        <?php endforeach; ?>
                    </select>
                </div>
                <button type="submit" class="buy-btn">PLACE ORDER</button>
            </form>
            
            <?php if (isset($order_result)): ?>
                <div class="result-box">
                    <pre>
> Processing order...
> <?php echo $order_result; ?>
                    </pre>
                </div>
            <?php endif; ?>
        </main>
        
        <footer>
            <p>Payments accepted in XMR - No refunds</p>
        </footer>
    </div>
</body>
</html>
