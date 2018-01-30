package com.example.websocket.stock.client;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.springframework.messaging.Message;
import org.springframework.messaging.converter.MappingJackson2MessageConverter;
import org.springframework.messaging.simp.stomp.StompCommand;
import org.springframework.messaging.simp.stomp.StompHeaders;
import org.springframework.messaging.simp.stomp.StompSession;
import org.springframework.messaging.simp.stomp.StompSessionHandler;
import org.springframework.stereotype.Service;
import org.springframework.web.socket.client.WebSocketClient;
import org.springframework.web.socket.client.standard.StandardWebSocketClient;
import org.springframework.web.socket.messaging.WebSocketStompClient;
import java.lang.reflect.Type;
import java.util.concurrent.ExecutionException;


/*
 * Tutorial: http://www.baeldung.com/websockets-api-java-spring-client
 */

@Service
public class IexWebsocketClient {
    protected Log logger = LogFactory.getLog(IexWebsocketClient.class);

    public IexWebsocketClient() throws InterruptedException, ExecutionException {
        logger.info("Entered IexWebSocketClient constructor");
        String URL = "wss://ws-api.iextrading.com/1.0/tops";
        WebSocketClient client = new StandardWebSocketClient();

        WebSocketStompClient stompClient = new WebSocketStompClient(client);
        stompClient.setMessageConverter(new MappingJackson2MessageConverter());

        StompSessionHandler sessionHandler = new StompSessionHandler() {
            @Override
            public void afterConnected(
                    StompSession session, StompHeaders connectedHeaders) {
                logger.info("Websocket connection accepted. Subscribing... ");
                session.send("subscribe", "snap,fb,aig+");
            }

            @Override
            public void handleFrame(StompHeaders headers, Object payload) {
                Message msg = (Message) payload;
                logger.info("Received : " + msg.toString()+ " from : " + msg.getHeaders().toString());
            }

            @Override
            public void handleException(StompSession stompSession, StompCommand stompCommand, StompHeaders stompHeaders, byte[] bytes, Throwable throwable) {

            }

            @Override
            public void handleTransportError(StompSession stompSession, Throwable throwable) {

            }

            @Override
            public Type getPayloadType(StompHeaders stompHeaders) {
                return null;
            }
        };

        stompClient.connect(URL, sessionHandler);
        logger.info("Exiting IexWebSocketClient constructor");
    }
}
