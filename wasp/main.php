<?php
require __DIR__ . '/vendor/autoload.php';

$dotenv = Dotenv\Dotenv::createImmutable(__DIR__); // Or createUnsafeImmutable if needed
$dotenv->load();

$verifyToken = $_ENV['WHATSAPP_VERIFY_TOKEN'];

$client = OpenAI::factory()
    ->withHttpClient($httpClient = new \GuzzleHttp\Client(['timeout' => 30, 'verify' => false]))
    ->withApiKey($_ENV['GEMINI_API_KEY'])
    ->withBaseUri('https://generativelanguage.googleapis.com/v1beta')
    ->make();
  
function newPayload($to, $type, $content){
    return [
        'messaging_product' => 'whatsapp',
        'to' => $to,
        'type' => $type,
        $type => $content
    ];
}
function sendPayload($payload){
    $URL = 'https://graph.facebook.com/v22.0/895322046993986/messages';
    $accessToken = $_ENV['WHATSAPP_API'];

    $client = new \GuzzleHttp\Client(['timeout' => 30, 'verify' => false]);
    
    try {
        $res = $client->post($URL, [
            'headers' => [
                'Authorization' => 'Bearer ' . $accessToken,
                'Content-Type' => 'application/json',
            ],
            'json' => $payload,
        ]);
    
        $httpCode = $res->getStatusCode();
        $response = (string) $res->getBody();
        $err = null;
    } catch (\GuzzleHttp\Exception\RequestException $e) {
        $err = $e->getMessage();
        if ($e->hasResponse()) {
            $response = (string) $e->getResponse()->getBody();
            $httpCode = $e->getResponse()->getStatusCode();
        } else {
            $response = null;
            $httpCode = 500;
        }
    }
    echo $httpCode;
    $logFile = __DIR__ . '/log.txt';
    @file_put_contents($logFile, $response."-".$err, FILE_APPEND | LOCK_EX);
}

function initMessage(){
    $to = '51997938975';
    $type = 'template';
    $content = [
        'name' => 'hello_world',
        'language' => ['code' => 'en_US']
    ];
    $payload = newPayload($to, $type, $content);
    sendPayload($payload);
}
function answerLLM($client, $prompt){
    $response = $client->chat()->create([
        'model' => 'gemini-2.5-flash-lite', // Use a compatible Gemini/Gemma model
        'messages' => [
            ['role' => 'system', 'content' => 'You are a helpful assistant.'],
            ['role' => 'user', 'content' => $prompt],
        ],
    ]);
    return $response->choices[0]->message->content;
}

// --- Lógica del Webhook ---
$uri = $_SERVER['REQUEST_URI'];
$requestMethod = $_SERVER['REQUEST_METHOD'];

if ($uri === '/test' && $requestMethod === 'GET') {
    echo "<h1>Bienvenido a mi aplicación PHP!</h1>";
    return;
}
if ($uri === '/init' && $requestMethod === 'GET') {
    initMessage();
    return;
}
if ($requestMethod === 'GET') {
    $mode = $_GET['hub_mode'] ?? null;
    $challenge = $_GET['hub_challenge'] ?? null;
    $token = $_GET['hub_verify_token'] ?? null;

    if ($mode === 'subscribe' && $token === $verifyToken) {
        header('Content-Type: text/plain');
        http_response_code(200);
        
        echo $challenge;
    } else {
        http_response_code(403);
    }
} elseif ($requestMethod === 'POST') {
    $input = file_get_contents('php://input');
    $body = json_decode($input, true);
    // Log raw request and parsed data to log.txt
    $logFile = __DIR__ . '/log.txt';
    $entry = json_encode($body, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . PHP_EOL;

    @file_put_contents($logFile, $entry, FILE_APPEND | LOCK_EX);

    $timestamp = date('Y-m-d H:i:s');
    $data = $body['entry']['0']['changes'][0]['value']['messages'][0];
    $to = $data['from'] ?? '';
    if(!$to){
        return;
    }
    $type = 'text';
    
    $text = $data['text']['body'] ?? '-';
    
    $content = [
        'body' => answerLLM($client, $text)
    ];
    $payload = newPayload($to, $type, $content);
    sendPayload($payload);
} else {
    // Método no soportado
    http_response_code(405);
    header('Allow: GET, POST');
}


//print_r(answerLLM($client, "Hola, ¿cómo estás?"));
//die(0);