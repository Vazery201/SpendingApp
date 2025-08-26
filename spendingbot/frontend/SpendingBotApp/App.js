// App.js
import React, { useEffect, useState, useCallback } from 'react';
import { SafeAreaView, View, Text, Button, FlatList, ActivityIndicator, StyleSheet, Alert } from 'react-native';
import { PlaidLink } from 'react-native-plaid-link-sdk';
import { NativeModules, Platform } from 'react-native';
console.log('PlaidLink typeof:', typeof PlaidLink);
console.log('RNLinksdk present?', !!NativeModules.RNLinksdk);

console.log('PlaidLink value:', typeof PlaidLink, PlaidLink && Object.keys(PlaidLink));
console.log('NativeModules present:', Object.keys(NativeModules));

const rnPlaid = NativeModules.RNLinksdk; // iOS native module name
console.log('RNLinksdk present?', !!rnPlaid, rnPlaid);

const BASE_URL = 'http://127.0.0.1:8000';
const CLIENT_USER_ID = 'demo-user';

export default function App() {
    const [linkToken, setLinkToken] = useState(null);
    const [loadingToken, setLoadingToken] = useState(false);
    const [status, setStatus] = useState('Idle');
    const [txns, setTxns] = useState([]);
    const [busy, setBusy] = useState(false);

    const fetchLinkToken = useCallback(async () => {
        try {
            setLoadingToken(true);
            setStatus('Creating link token…');
            const res = await fetch(`${BASE_URL}/plaid/create_link_token`, { method: 'POST' });
            if (!res.ok) throw new Error(`link_token HTTP ${res.status}`);
            const json = await res.json();
            setLinkToken(json.link_token);
            setStatus('Ready to link');
        } catch (e) {
            console.error(e);
            Alert.alert('Error', `Failed to create link token:\n${String(e.message || e)}`);
            setStatus('Error creating link token');
        } finally {
            setLoadingToken(false);
        }
    }, []);

    useEffect(() => {
        fetchLinkToken();
    }, [fetchLinkToken]);

    const exchangeAndFetch = useCallback(async (publicToken) => {
        try {
            setBusy(true);
            setStatus('Exchanging public token…');

            // Our backend expects JSON body for exchange
            const ex = await fetch(`${BASE_URL}/plaid/exchange_public_token`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ public_token: publicToken, client_user_id: CLIENT_USER_ID }),
            });
            if (!ex.ok) {
                const text = await ex.text();
                throw new Error(`exchange HTTP ${ex.status} - ${text}`);
            }
            setStatus('Fetching transactions…');

            const tx = await fetch(`${BASE_URL}/plaid/transactions?client_user_id=${encodeURIComponent(CLIENT_USER_ID)}&days=30`);
            if (!tx.ok) throw new Error(`transactions HTTP ${tx.status}`);
            const data = await tx.json();
            const items = Array.isArray(data) ? data : (data.transactions || data.results || []);
            setTxns(items);
            setStatus(`Fetched ${items.length} transactions`);
        } catch (e) {
            console.error(e);
            Alert.alert('Error', String(e.message || e));
            setStatus('Error');
        } finally {
            setBusy(false);
        }
    }, []);

    return (
        <SafeAreaView style={styles.safe}>
            <View style={styles.header}>
                <Text style={styles.title}>SpendingBot</Text>
                <Text style={styles.sub}>{status}</Text>
            </View>

            {loadingToken && <ActivityIndicator size="large" />}

            {!loadingToken && !linkToken && (
                <Button title="Retry: Get Link Token" onPress={fetchLinkToken} />
            )}

            {PlaidLink ? (
                <PlaidLink
                    tokenConfig={{ token: linkToken }}
                    onSuccess={({ publicToken }) => exchangeAndFetch(publicToken)}
                    onExit={() => Alert.alert('Plaid', 'Link flow exited.')}
                >
                    <View style={styles.linkBtn}>
                        <Text style={styles.linkBtnText}>{busy ? 'Working…' : 'Connect a bank'}</Text>
                    </View>
                </PlaidLink>
            ) : (
                <View style={[styles.linkBtn, { borderColor: 'red' }]}>
                    <Text style={styles.linkBtnText}>
                        Plaid module not available. Recheck import & run pod install + full rebuild.
                    </Text>
                </View>
            )}

            <View style={styles.listWrap}>
                {txns.length > 0 ? (
                    <FlatList
                        data={txns.slice(0, 25)}
                        keyExtractor={(item, idx) => String(item.transaction_id || item.id || idx)}
                        renderItem={({ item }) => (
                            <View style={styles.row}>
                                <Text style={styles.rowTitle}>{item.name || item.merchant_name || 'Transaction'}</Text>
                                <Text>{item.date || item.authorized_date}</Text>
                                <Text style={styles.amount}>
                                    {item.amount != null ? `$${Number(item.amount).toFixed(2)}` : ''}
                                </Text>
                            </View>
                        )}
                    />
                ) : (
                    <Text style={{ opacity: 0.6 }}>No transactions yet.</Text>
                )}
            </View>
        </SafeAreaView>
    );
}

const styles = StyleSheet.create({
    safe: { flex: 1, padding: 16, gap: 16 },
    header: { gap: 6 },
    title: { fontSize: 24, fontWeight: '800' },
    sub: { opacity: 0.7 },
    linkBtn: { marginTop: 8, padding: 14, borderRadius: 12, borderWidth: 1, alignItems: 'center' },
    linkBtnText: { fontWeight: '700' },
    listWrap: { flex: 1, marginTop: 16 },
    row: { paddingVertical: 10, borderBottomWidth: StyleSheet.hairlineWidth, gap: 4 },
    rowTitle: { fontWeight: '600' },
    amount: { fontVariant: ['tabular-nums'] },
});
