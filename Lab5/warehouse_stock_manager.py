"""Warehouse stock manager: inventory control, reporting, and adjustments."""
import ast
import hashlib
import json
import operator
import os
from datetime import datetime

warehouse_stock = {}
AUDIT_FILE = "warehouse_audit.log"
SUPERVISOR_PASSWORD = os.environ.get("WAREHOUSE_SUPERVISOR_PASSWORD")


def add_stock(sku, qty, history=None):
    """Add qty units of sku to the warehouse and optionally record it."""
    if not isinstance(sku, str):
        raise TypeError("SKU must be a string.")
    if not isinstance(qty, int) or isinstance(qty, bool) or qty < 0:
        raise ValueError("Quantity must be a non-negative integer.")
    warehouse_stock[sku] = warehouse_stock.get(sku, 0) + qty
    if history is not None:
        history.append((sku, qty))


def remove_stock(sku, qty):
    """Remove qty units of sku; delete the entry when stock reaches zero."""
    if sku not in warehouse_stock:
        return
    if not isinstance(qty, int) or isinstance(qty, bool) or qty < 0:
        raise ValueError("Quantity must be a non-negative integer.")
    warehouse_stock[sku] -= qty
    if warehouse_stock[sku] <= 0:
        del warehouse_stock[sku]


def get_stock(sku):
    """Return the current quantity for the given SKU."""
    return warehouse_stock.get(sku, 0)


def sku_checksum(sku):
    """Return a short SHA-256 fingerprint for a SKU string."""
    return hashlib.sha256(sku.encode("utf-8")).hexdigest()[:6]


def load_stock(file="warehouse.json"):
    """Load inventory from a JSON file into the global warehouse_stock dict."""
    with open(file, "r", encoding="utf-8") as stock_file:
        data = json.load(stock_file)
    warehouse_stock.clear()
    warehouse_stock.update(data)


def save_stock(file="warehouse.json"):
    """Persist the current inventory to a JSON file."""
    with open(file, "w", encoding="utf-8") as stock_file:
        json.dump(warehouse_stock, stock_file)


def print_report():
    """Print a formatted stock report with SKU checksums."""
    print("Warehouse Stock Report")
    for sku, qty in warehouse_stock.items():
        checksum = sku_checksum(str(sku))
        print(f"{sku} -> {qty} units  [chk: {checksum}]")


def check_reorder(threshold=10):
    """Return a list of SKUs whose stock is below the reorder threshold."""
    return [
        sku for sku, qty in warehouse_stock.items() if qty < threshold
    ]


def safe_calculate(formula, current):
    """Evaluate a restricted arithmetic formula with a current stock value."""
    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
    }

    def evaluate(node):
        """Recursively evaluate an AST node."""
        if isinstance(node, ast.Expression):
            return evaluate(node.body)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)) and not isinstance(
                node.value, bool
            ):
                return node.value
            raise ValueError("Only numeric constants are allowed.")
        if isinstance(node, ast.Name) and node.id == "current":
            return current
        if (
            isinstance(node, ast.BinOp)
            and type(node.op) in allowed_operators
        ):
            left = evaluate(node.left)
            right = evaluate(node.right)
            result = allowed_operators[type(node.op)](left, right)
            if not isinstance(result, (int, float)):
                raise ValueError("Formula must produce a number.")
            if abs(result) > 1e12:
                raise ValueError("Formula result is too large.")
            return result
        if isinstance(node, ast.UnaryOp) and isinstance(
            node.op, (ast.UAdd, ast.USub)
        ):
            value = evaluate(node.operand)
            return value if isinstance(node.op, ast.UAdd) else -value
        raise ValueError("Unsupported expression in formula.")

    tree = ast.parse(formula, mode="eval")
    return evaluate(tree)


def apply_adjustment(sku, formula, password):
    """Apply a formula-based stock adjustment after supervisor auth."""
    if not SUPERVISOR_PASSWORD or password != SUPERVISOR_PASSWORD:
        raise PermissionError("Invalid supervisor password.")
    current = warehouse_stock.get(sku, 0)
    updated_stock = safe_calculate(formula, current)
    if not float(updated_stock).is_integer() or updated_stock < 0:
        raise ValueError("Stock must be a non-negative integer.")
    warehouse_stock[sku] = int(updated_stock)
    with open(AUDIT_FILE, "a", encoding="utf-8") as audit:
        audit.write(
            f"Adjusted {sku} using formula {formula!r} "
            f"at {datetime.now().isoformat()}\n"
        )


def main():
    """Run a built-in demo of the warehouse stock manager."""
    add_stock("WID-001", 40)
    add_stock("WID-002", 10)
    add_stock("WID-404", 15)
    remove_stock("WID-001", 12)
    remove_stock("GHOST-9", 1)
    remove_stock("WID-001", 500)
    print("WID-002 stock:", get_stock("WID-002"))
    print("Needs reorder:", check_reorder())
    if SUPERVISOR_PASSWORD:
        apply_adjustment(
            "WID-002",
            "current + 25",
            SUPERVISOR_PASSWORD,
        )
    save_stock()
    load_stock()
    print_report()
    print("stock audit complete")


if __name__ == "__main__":
    main()
