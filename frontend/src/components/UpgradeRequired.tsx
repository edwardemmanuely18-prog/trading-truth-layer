"use client";

type Props = {
    open: boolean;
    feature: string;
    onClose: () => void;
};

export default function UpgradeRequired({
    open,
}: Props) {

    if (!open) {
        return null;
    }

    return null;

}